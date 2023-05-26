import logging
import os
import tempfile
import pandas
from flask import current_app
from sqlalchemy import Select
from sqlalchemy.orm import selectinload,contains_eager
from werkzeug.utils import secure_filename

from app import db
from app.exceptions.exceptions import InvalidFile
from app.models.audit.AuditUpdateData import AuditUpdateData
from app.models.enums.DataType import DataType
from app.models.financial.MontantFinancialAe import MontantFinancialAe
from app.models.financial.FinancialCp import FinancialCp
from app.models.financial.FinancialAe import FinancialAe
from app.models.refs.code_programme import CodeProgramme
from app.models.refs.commune import Commune
from app.models.refs.referentiel_programmation import ReferentielProgrammation
from app.models.refs.siret import Siret
from app.models.refs.theme import Theme
from app.services import allowed_file, FileNotAllowedException
from app.services.code_geo import BuilderCodeGeo


def import_ae(file_ae, source_region:str, annee: int, force_update: bool, username=""):
    save_path = _check_file_and_save(file_ae)
    _check_file(save_path, FinancialAe.get_columns_files_ae())

    logging.info(f'[IMPORT FINANCIAL] Récupération du fichier {save_path}')
    from app.tasks.import_financial_tasks import import_file_ae_financial
    task = import_file_ae_financial.delay(str(save_path), source_region, annee, force_update)
    db.session.add(AuditUpdateData(username=username, filename=file_ae.filename, data_type=DataType.FINANCIAL_DATA_AE))
    db.session.commit()
    return task


def import_cp(file_cp, source_region:str, annee: int, username=""):
    save_path = _check_file_and_save(file_cp)
    _check_file(save_path, FinancialCp.get_columns_files_cp())

    logging.info(f'[IMPORT FINANCIAL] Récupération du fichier {save_path}')
    from app.tasks.import_financial_tasks import import_file_cp_financial
    task = import_file_cp_financial.delay(str(save_path), source_region, annee)
    db.session.add(AuditUpdateData(username=username, filename=file_cp.filename, data_type=DataType.FINANCIAL_DATA_CP))
    db.session.commit()
    return task


def get_financial_data_ae(code_programme: list = None, theme: list = None, siret_beneficiaire: list = None, annee: list = None,
                          code_geo: list = None, pageNumber=1, limit=500):

    if (code_geo is not None):
        (type, code_geo)  = BuilderCodeGeo.build_list_code_geo(code_geo)

    stmt = _build_select_financial_ae()

    stmt = stmt.join(FinancialAe.ref_siret.and_(Siret.code.in_(siret_beneficiaire))) if siret_beneficiaire is not None else stmt.join(Siret)
    stmt = stmt.join(Siret.ref_commune)

    if code_programme is not None:
        stmt = stmt.join(FinancialAe.ref_programme.and_(CodeProgramme.code.in_(code_programme))).join(CodeProgramme.theme_r)
    elif theme is not None:
        stmt = stmt.join(FinancialAe.ref_programme).join(CodeProgramme.theme_r.and_(Theme.label.in_(theme)))
    else:
        stmt = stmt.join(FinancialAe.ref_programme).join(CodeProgramme.theme_r)

    if annee is not None:
        stmt = stmt.where(FinancialAe.annee.in_(annee))

    stmt = stmt.options(
            contains_eager(FinancialAe.ref_programme).load_only(CodeProgramme.label).contains_eager(CodeProgramme.theme_r).load_only(Theme.label),
            contains_eager(FinancialAe.ref_siret).load_only(Siret.code, Siret.denomination).contains_eager(Siret.ref_commune).load_only(Commune.label_commune))

    page_result = db.paginate(stmt, per_page=limit, page=pageNumber, error_out=False)

    return page_result


def _build_select_financial_ae() -> Select:
    '''
    Construit la selection des données fiancières
    :return: Select statement
    '''

    return db.select(FinancialAe)\
        .options(db.defer(FinancialAe.source_region),
                 db.defer(FinancialAe.groupe_marchandise),
                 db.defer(FinancialAe.compte_budgetaire),
                 selectinload(FinancialAe.montant_ae).load_only(MontantFinancialAe.montant),
                 selectinload(FinancialAe.financial_cp).load_only(FinancialCp.montant),
                 db.defer(FinancialAe.contrat_etat_region))


def _check_file_and_save(file) -> str:
    if file.filename == '':
        raise InvalidFile(message="Pas de fichier")

    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)
        if 'UPLOAD_FOLDER' in current_app.config:
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        else:
            save_path = os.path.join(tempfile.gettempdir(), filename)
        file.save(save_path)
        return save_path
    else:
        logging.error(f'[IMPORT FINANCIAL] Fichier refusé {file.filename}')
        raise FileNotAllowedException(message='le fichier n\'est pas un csv')



def _check_file(fichier, columns_name):

    try:
        check_column = pandas.read_csv(fichier, sep=",", skiprows=8, nrows=5)
    except Exception:
        logging.exception(msg="[CHECK FILE] Erreur de lecture du fichier")
        raise FileNotAllowedException(message="Erreur de lecture du fichier")

    # check nb colonnes
    if len(check_column.columns) != len(columns_name):
        raise InvalidFile(message="Le fichier n'a pas les bonnes colonnes")

    try:
        data_financial = pandas.read_csv(fichier, sep=",", skiprows=8, nrows=5,
                                      names=columns_name,
                                       dtype={'n_ej': str, 'n_poste_ej': str,
                                                     'fournisseur_titulaire': str,
                                                     'siret': str})
    except Exception:
        logging.exception(msg="[CHECK FILE] Erreur de lecture du fichier")
        raise FileNotAllowedException(message="Erreur de lecture du fichier")

    if data_financial.isnull().values.any():
        raise InvalidFile(message="Le fichier contient des valeurs vides")



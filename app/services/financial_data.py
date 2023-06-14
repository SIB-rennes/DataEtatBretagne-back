import logging
import os
import tempfile
import pandas
from flask import current_app
from werkzeug.utils import secure_filename

from app import db
from app.exceptions.exceptions import InvalidFile, FileNotAllowedException
from app.models.audit.AuditUpdateData import AuditUpdateData
from app.models.enums.DataType import DataType
from app.models.financial.Ademe import Ademe

from app.models.financial.FinancialCp import FinancialCp
from app.models.financial.FinancialAe import FinancialAe
from app.models.refs.domaine_fonctionnel import DomaineFonctionnel
from app.models.refs.referentiel_programmation import ReferentielProgrammation
from app.models.refs.siret import Siret
from app.services import BuilderStatementFinancial
from app.services.code_geo import BuilderCodeGeo
from app.services.file_service import allowed_file


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


def import_ademe(file_ademe, username=""):
    save_path = _check_file_and_save(file_ademe)

    logging.info(f'[IMPORT ADEME] Récupération du fichier {save_path}')
    from app.tasks.import_financial_tasks import import_file_ademe
    task = import_file_ademe.delay(str(save_path))
    db.session.add(AuditUpdateData(username=username, filename=file_ademe.filename, data_type=DataType.ADEME))
    db.session.commit()
    return task

def get_financial_ae(id: int) -> FinancialAe:
    query_select = BuilderStatementFinancial().select_ae() \
        .join_filter_siret() \
        .join_filter_programme_theme()\
        .join_commune().by_ae_id(id).options_select_load()

    result = query_select.do_single()
    return result

def search_ademe(siret_beneficiaire: list = None, code_geo: list = None, annee: list = None, page_number=1, limit=500):
    query = db.select(Ademe)
    query = query.join(Ademe.ref_siret_beneficiaire.and_(
        Siret.code.in_(siret_beneficiaire))) if siret_beneficiaire is not None else query.join(Siret,
                                                                                               Ademe.ref_siret_beneficiaire)
    query = query.join(Siret.ref_categorie_juridique)

    #utilisation du builder
    query_ademe = BuilderStatementFinancial(query)

    if code_geo is not None:
        (type_geo, list_code_geo) = BuilderCodeGeo().build_list_code_geo(code_geo)
        query_ademe.where_geo(type_geo, list_code_geo)
    else:
        query_ademe.join_commune()

    if annee is not None:
        query_ademe.where_custom( db.func.extract('year', Ademe.date_convention).in_(annee))

    page_result = query_ademe.do_paginate(limit, page_number)
    return page_result


def get_ademe(id: int) -> Ademe:
    query = db.select(Ademe).join(Siret,Ademe.ref_siret_beneficiaire).join(Siret.ref_categorie_juridique)

    result = BuilderStatementFinancial(query).join_commune().where_custom(Ademe.id == id).do_single()
    return result

def search_financial_data_ae(
        code_programme: list = None, theme: list = None, siret_beneficiaire: list = None, annee: list = None,
        domaine_fonctionnel: list = None, referentiel_programmation: list = None,
        code_geo: list = None, page_number=1, limit=500):


    query_siret = BuilderStatementFinancial().select_ae()\
        .join_filter_siret(siret_beneficiaire)\
        .join_filter_programme_theme(code_programme, theme)

    if code_geo is not None:
        (type_geo, list_code_geo) = BuilderCodeGeo().build_list_code_geo(code_geo)
        query_siret.where_geo_ae(type_geo, list_code_geo)
    else :
        query_siret.join_commune()
    
    if domaine_fonctionnel is not None:
        query_siret.where_custom(DomaineFonctionnel.code.in_(domaine_fonctionnel))
    
    if referentiel_programmation is not None:
        query_siret.where_custom(ReferentielProgrammation.code.in_(referentiel_programmation))

    page_result = query_siret.where_annee(annee).options_select_load().do_paginate(limit, page_number)
    return page_result


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



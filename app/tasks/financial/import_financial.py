import datetime
import shutil
from collections import namedtuple
import json
from celery import current_task, subtask
from flask import current_app
from sqlalchemy import delete, update
from app import celeryapp, db
from app.exceptions.exceptions import FinancialException
import sqlalchemy.exc
from app.models.financial import FinancialData
from app.models.financial.Ademe import Ademe
from app.models.financial.FinancialAe import FinancialAe
from app.models.financial.FinancialCp import FinancialCp
from app.models.refs.centre_couts import CentreCouts
from app.models.refs.code_programme import CodeProgramme
from app.models.refs.domaine_fonctionnel import DomaineFonctionnel
from app.models.refs.fournisseur_titulaire import FournisseurTitulaire
from app.models.refs.groupe_marchandise import GroupeMarchandise
from app.models.refs.localisation_interministerielle import LocalisationInterministerielle
from app.models.refs.referentiel_programmation import ReferentielProgrammation
from app.services.siret import check_siret
from app.tasks import limiter_queue

from collections import namedtuple
import pandas
import json
import requests
import tempfile

import os

from app.tasks.financial import logger
from app.tasks.financial.errors import _handle_exception_import


@limiter_queue(queue_name='line')
def _send_subtask_financial_ae(line, index, force_update):
    subtask("import_line_financial_ae").delay(line, index, force_update)


celery = celeryapp.celery
@celery.task(bind=True, name='import_file_ae_financial')
def import_file_ae_financial(self, fichier, source_region: str, annee: int, force_update: bool):
    # get file
    logger.info(f'[IMPORT][FINANCIAL][AE] Start for region {source_region}, year {annee}, file {fichier}')
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    move_folder = current_app.config['UPLOAD_FOLDER'] + "/save/"
    try:
        data_chorus_chunk = pandas.read_csv(fichier, sep=",", skiprows=8, names=FinancialAe.get_columns_files_ae(),
                                      dtype={'programme': str, 'n_ej': str, 'n_poste_ej': int,
                                             'fournisseur_titulaire': str,
                                             'siret': str}, chunksize=1000)
        series = pandas.Series({ f'{FinancialAe.annee.key}' : annee, f'{FinancialAe.source_region.key}': source_region})

        for chunk in data_chorus_chunk:
            for index, line in chunk.iterrows():
                _send_subtask_financial_ae(line.append(series).to_json(), index, force_update)

        move_folder = os.path.join(move_folder,timestamp)
        if not os.path.exists(move_folder):
            os.makedirs(move_folder)
        logger.info(f'[IMPORT][FINANCIAL][AE] Save file {fichier} in {move_folder}')
        shutil.move(fichier, move_folder)
        logger.info('[IMPORT][FINANCIAL][AE] End')

        return True
    except Exception as e:
        logger.exception(f"[IMPORT][FINANCIAL][AE] Error lors de l'import du fichier {fichier} chorus")
        raise e


LineImportTechInfo = namedtuple('LineImportTechInfo', ['file_import_taskid', 'lineno'])


@limiter_queue(queue_name='line')
def _send_subtask_financial_cp(line, index, source_region, annee, tech_info: LineImportTechInfo):
    subtask("import_line_financial_cp").delay(line, index, source_region, annee, tech_info)


def _delete_cp(annee: int, source_region: str):
    """
    Supprimes CP d'une année comptable
    :param annee:
    :param source_region:
    :return:
    """
    stmt = (
        delete(FinancialCp).
        where(FinancialCp.annee == annee).
        where(FinancialCp.source_region == source_region)
    )
    db.session.execute(stmt)
    db.session.commit()


@celery.task(bind=True, name='import_file_cp_financial')
def import_file_cp_financial(self, fichier, source_region: str, annee: int):
    # get file
    logger.info(f'[IMPORT][FINANCIAL][CP] Start for region {source_region}, year {annee}, file {fichier}')
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    move_folder = current_app.config['UPLOAD_FOLDER'] + "/save/"

    try:
        current_taskid = current_task.request.id
        data_chorus_chunk = pandas.read_csv(fichier, sep=",", skiprows=8, names=FinancialCp.get_columns_files_cp(),
                                      dtype={'programme': str, 'n_ej': str, 'n_poste_ej': str, 'n_dp': str,
                                             'fournisseur_paye': str,
                                             'siret': str}, chunksize=1000)
        _delete_cp(annee, source_region)

        i = 0
        for chunk in data_chorus_chunk:
            for index, line in chunk.iterrows():
                i += 1
                tech_info = LineImportTechInfo(current_taskid, i)
                _send_subtask_financial_cp(line.to_json(), index, source_region, annee, tech_info)


        move_folder = os.path.join(move_folder, timestamp)
        if not os.path.exists(move_folder):
            os.makedirs(move_folder)
        logger.info(f'[IMPORT][FINANCIAL][CP] Save file {fichier} in {move_folder}')
        shutil.move(fichier, move_folder)

        logger.info('[IMPORT][FINANCIAL][CP] End')
        return True
    except Exception as e:
        logger.exception(f"[IMPORT][FINANCIAL][CP] Error lors de l'import du fichier {fichier} chorus")
        raise e


def _check_ref(model, code):
    instance = db.session.query(model).filter_by(code=str(code)).one_or_none()
    if not instance:
        instance = model(**{'code':code})
        logger.info(f'[IMPORT][REF] Ajout ref {model.__tablename__} code {code}')
        try:
            db.session.add(instance)
            db.session.commit()
        except Exception as e:  # The actual exception depends on the specific database so we catch all exceptions. This is similar to the official documentation: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html
            logger.exception(f"[IMPORT][CHORUS] Error sur ajout ref {model.__tablename__} code {code}")
            raise e


def _check_insert_update_financial(financial_ae: FinancialData | None, line,force_update: bool) -> FinancialData | bool:
    '''
    :param financial_ae: l'instance financière déjà présente ou non
    :param force_update:
    :return: True -> Objet à créer
             False -> rien à faire
             Instance chorus -> Objet à update
    '''

    if financial_ae:
        if force_update:
            logger.info('[IMPORT][FINANCIAL] Doublon trouvé, Force Update')
            return financial_ae
        if financial_ae.should_update(line):
            logger.info('[IMPORT][FINANCIAL] Doublon trouvé, MAJ à faire')
            return financial_ae
        else:
            logger.info('[IMPORT][FINANCIAL] Doublon trouvé, Pas de maj')
            return False
    return True


def _insert_financial_data(data: FinancialData) -> FinancialData:
    db.session.add(data)
    logger.info('[IMPORT][FINANCIAL] Ajout ligne financière')
    db.session.commit()
    return data


def _update_financial_data(data, financial: FinancialData) -> FinancialData:
    financial.update_attribute(data)
    logger.info('[IMPORT][FINANCIAL] Update ligne financière')
    db.session.commit()
    return financial


def _make_link_ae_to_cp(id_financial_ae: int, n_ej: str, n_poste_ej: int):
    """
    Lance une requête update pour faire le lien entre une AE et des CP
    :param id_financial_ae: l'id d'une AE
    :param n_ej : le numero d'ej
    :parman n_poste_ej : le poste ej
    :return:
    """

    stmt = (
        update(FinancialCp).
        where(FinancialCp.n_ej == n_ej).
        where(FinancialCp.n_poste_ej == n_poste_ej).
        values(id_ae=id_financial_ae)
    )
    db.session.execute(stmt)
    db.session.commit()


@celery.task(bind=True, name='import_line_financial_ae', autoretry_for=(FinancialException,), retry_kwargs={'max_retries': 4, 'countdown': 10})
@_handle_exception_import('FINANCIAL_AE')
def import_line_financial_ae(self, dict_financial: str, index: int, force_update: bool):
    line = json.loads(dict_financial)
    try :
        financial_ae_instance = db.session.query(FinancialAe).filter_by(n_ej=line[FinancialAe.n_ej.key],
                                                  n_poste_ej=line[FinancialAe.n_poste_ej.key]).one_or_none()
        financial_instance = _check_insert_update_financial(financial_ae_instance,line, force_update)
    except sqlalchemy.exc.OperationalError as o:
        logger.exception(f"[IMPORT][CHORUS] Erreur index {index} sur le check ligne chorus")
        raise FinancialException(o) from o


    if financial_instance != False:

        new_ae = FinancialAe(**line)

        _check_ref(CodeProgramme, new_ae.programme)
        _check_ref(CentreCouts, new_ae.centre_couts)
        _check_ref(DomaineFonctionnel, new_ae.domaine_fonctionnel)
        _check_ref(FournisseurTitulaire, new_ae.fournisseur_titulaire)
        _check_ref(GroupeMarchandise, new_ae.groupe_marchandise)
        _check_ref(LocalisationInterministerielle, new_ae.localisation_interministerielle)
        _check_ref(ReferentielProgrammation, new_ae.referentiel_programmation)

        # SIRET
        check_siret(new_ae.siret)

        # CHORUS
        new_financial_ae = None
        if financial_instance == True:
            new_financial_ae = _insert_financial_data(new_ae)
        else:
            new_financial_ae = _update_financial_data(line, financial_instance)

        _make_link_ae_to_cp(new_financial_ae.id, new_financial_ae.n_ej, new_financial_ae.n_poste_ej)


def _get_ae_for_cp(n_ej: str, n_poste_ej: int) -> int | None:
    """
    Récupère le bon AE pour le lié au CP
    :param n_ej : le numero d'ej
    :parman n_poste_ej : le poste ej
    :return:
    """
    if n_ej is None or n_poste_ej is None :
        return None

    financial_ae = FinancialAe.query.filter_by(n_ej=str(n_ej), n_poste_ej=int(n_poste_ej)).one_or_none()
    return financial_ae.id if financial_ae is not None else None


@celery.task(bind=True, name='import_line_financial_cp')
@_handle_exception_import('FINANCIAL_CP')
def import_line_financial_cp(self, data_cp, index, source_region: str, annee: int, tech_info_list: list):

    tech_info = LineImportTechInfo(*tech_info_list)

    line = json.loads(data_cp)

    new_cp = FinancialCp(line, source_region=source_region, annee=annee)
    new_cp.file_import_taskid = tech_info.file_import_taskid
    new_cp.file_import_lineno = tech_info.lineno

    _check_ref(CodeProgramme, new_cp.programme)
    _check_ref(CentreCouts, new_cp.centre_couts)
    _check_ref(DomaineFonctionnel, new_cp.domaine_fonctionnel)
    _check_ref(FournisseurTitulaire, new_cp.fournisseur_paye)
    _check_ref(GroupeMarchandise, new_cp.groupe_marchandise)
    _check_ref(LocalisationInterministerielle, new_cp.localisation_interministerielle)
    _check_ref(ReferentielProgrammation, new_cp.referentiel_programmation)

    # SIRET
    check_siret(new_cp.siret)

    # FINANCIAL_AE
    id_ae = _get_ae_for_cp(new_cp.n_ej, new_cp.n_poste_ej)
    new_cp.id_ae = id_ae
    _insert_financial_data(new_cp)

@limiter_queue(queue_name='file')
def _send_subtask_ademe_file(filepath: str):
    subtask("import_file_ademe").delay(filepath)

@limiter_queue(queue_name='line')
def _send_subtask_ademe(data_ademe: str, tech_info: LineImportTechInfo):
    subtask("import_line_ademe").delay(data_ademe, tech_info)


def _delete_ademe():
    """
    Supprime toutes les données ADEME
    :return:
    """
    stmt = delete(Ademe)
    db.session.execute(stmt)
    db.session.commit()

@celery.task(bind=True, name='import_file_ademe_from_website')
def import_file_ademe_from_website(self, url: str):

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                temp_file.write(chunk)
        
        logger.info(f"Fichier téléchargé. Import...")
        _send_subtask_ademe_file(temp_file.name)


@celery.task(bind=True, name='import_file_ademe')
def import_file_ademe(self, fichier):
    # get file
    logger.info(f'[IMPORT][ADEME] Start for file {fichier}')
    try:
        current_taskid = current_task.request.id
        data_ademe_chunk = pandas.read_csv(fichier, sep=",", skiprows=1, names=Ademe.get_columns_files(),
                                      dtype={'location_lat': float,'pourcentage_subvention':float, 'siret_beneficiaire': str,'siret_attribuant':str,
                                             'location_lon': float, 'idBeneficiaire': str,"notification_ue": str,
                                             'idAttribuant': str}, chunksize=1000)
        _delete_ademe()

        i = 0
        for chunk in data_ademe_chunk:
            for _,ademe_data in chunk.iterrows():
                i += 1
                tech_info = LineImportTechInfo(current_taskid, i)
                _send_subtask_ademe(ademe_data.to_json(), tech_info)

        logger.info('[IMPORT][ADEME] End')
        return True
    except Exception as e:
        logger.exception(f"[IMPORT][ADEME] Error lors de l'import du fichier ademe: {fichier}")
        raise e
    finally:
        os.remove(fichier)


@celery.task(bind=True, name='import_line_ademe')
@_handle_exception_import('ADEME')
def import_line_ademe(self, line_ademe: str, tech_info_list: list):

    logger.debug(f"[IMPORT][ADEME][LINE] Traitement de la ligne ademe: {tech_info_list}")
    logger.debug(f"[IMPORT][ADEME][LINE] Contenu de la ligne ADEME : {line_ademe}")
    logger.debug(f"[IMPORT][ADEME][LINE] Contenu du tech info      : {tech_info_list}")

    tech_info = LineImportTechInfo(*tech_info_list)

    line = json.loads(line_ademe)
    new_ademe = Ademe(line)
    new_ademe.file_import_taskid = tech_info.file_import_taskid
    new_ademe.file_import_lineno = tech_info.lineno

    logger.info(
        f'[IMPORT][ADEME] Tentative ligne Ademe referece decision {new_ademe.reference_decision}, beneficiaire {new_ademe.siret_beneficiaire}')

    # SIRET Attribuant
    check_siret(new_ademe.siret_attribuant)
    # SIRET beneficiaire
    check_siret(new_ademe.siret_beneficiaire)

    db.session.add(new_ademe)
    logger.info('[IMPORT][FINANCIAL] Ajout ligne financière')
    db.session.commit()

    logger.debug(f"[IMPORT][ADEME][LINE] Traitement de la ligne ademe: {tech_info_list}")
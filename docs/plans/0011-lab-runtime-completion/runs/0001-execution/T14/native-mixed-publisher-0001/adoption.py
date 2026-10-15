"""Explicit private Root assembly; no constructor on import or ambient defaults."""
from pathlib import Path
from .contracts import closed,need,sha,compact
from .software import SelectedSoftware
from .boundary import PublicationBoundary,OwnerPublicationGuard
from .receipt_store import ReceiptStore
from .gateway import NativeMixedPublisher
from .origins import require_original

def construct(packet,*,independent_packet_sha256,modules,read_public,objects,locks):
    closed(packet,('schema_version','status','boundary','boundary_sha256','receipt_root','receipt_root_identity','replay_root','replay_root_identity','review_sha256','identity_path','identity_sha256','selections','extension_packages','mirrors','native_selection','output_roles','authority_effect'))
    need(packet['schema_version']=='lab-T14-native-mixed-adoption/v1-candidate'and packet['status']=='independently-selected-active'and packet['authority_effect']=='none','closed active independent Root packet required')
    need(sha(compact(packet))==independent_packet_sha256,'independent Root packet pin differs')
    closed(objects,('original','promotion','ingress','parent','source_selection','authority','owner_selection','trust','response_raw','native_store','native_factory','source_guard','cut_reader','permission_guard'))
    need(packet['boundary']['operation']!='inspect-coupled-publication','cold-read-only packet cannot construct a new publication')
    software=SelectedSoftware(modules,read_public)
    require_original(software,objects['original'],'repository-publisher');require_original(software,objects['promotion'],'repository-promotion');require_original(software,objects['ingress'],'owner-ingress')
    software.function(objects['source_guard'])()
    need(software.function(objects['permission_guard'])()==packet['boundary']['permission_snapshot'],'actual original permission absent before protected preparation')
    need(software.function(objects['cut_reader'])()==packet['boundary']['source_cut'],'actual Source cut differs before protected preparation')
    # Root provides a previously prepared, exact human-reviewed review. Build
    # the same source/core review again before installing the live owner guard.
    software.function(objects['promotion'].prepare_promotion)
    prepared=objects['promotion'].prepare_promotion(objects['parent'],objects['source_selection'],packet['selections'],
        packet['identity_path'],packet['identity_sha256'],objects['authority'],extension_packages=packet['extension_packages'],mirrors=packet['mirrors'])
    need(sha(compact(prepared['review']))==packet['review_sha256'],'Root-selected real reviewed cores differ')
    ingress=objects['ingress'];software.function(ingress.verify_for_publication)
    response=ingress.parse(objects['response_raw'])
    owner=OwnerPublicationGuard(ingress,prepared['review'],response,objects['owner_selection'],objects['trust'])
    boundary=PublicationBoundary(software,objects['source_guard'],objects['cut_reader'],objects['permission_guard'],owner.check,
        packet['boundary'],independent_control_sha256=packet['boundary_sha256'],locks=locks)
    store=None;replay_store=None
    try:
        store=ReceiptStore(Path(packet['receipt_root']),tuple(packet['receipt_root_identity']),boundary)
        replay_store=ReceiptStore(Path(packet['replay_root']),tuple(packet['replay_root_identity']),boundary)
        return NativeMixedPublisher(store=store,replay_store=replay_store,boundary=boundary,original=objects['original'],promotion=objects['promotion'],ingress=ingress,
            parent=objects['parent'],source_selection=objects['source_selection'],selections=packet['selections'],identity_path=packet['identity_path'],
            identity_sha256=packet['identity_sha256'],authority=objects['authority'],owner_selection=objects['owner_selection'],trust=objects['trust'],
            response_raw=objects['response_raw'],native_store=objects['native_store'],native_factory=objects['native_factory'],native_selection=packet['native_selection'],
            output_roles=tuple(packet['output_roles']),extension_packages=packet['extension_packages'],mirrors=packet['mirrors'],expected_review_sha256=packet['review_sha256'])
    except BaseException:
        if replay_store is not None:replay_store.close()
        if store is not None:store.close()
        raise

def construct_cold_reader(packet,*,independent_packet_sha256,modules,read_public,objects,locks,current_recovery_guard):
    """Fresh explicit recovery authority; never re-open the old owner's lease.

    Root's selected recovery guard must verify the current actual permission
    and this exact immutable record. It is separate from historical owner
    verification, which cannot authorize any new write.
    """
    closed(packet,('schema_version','status','boundary','boundary_sha256','receipt_root','receipt_root_identity','replay_root','replay_root_identity','review_sha256','identity_path','identity_sha256','selections','extension_packages','mirrors','native_selection','output_roles','authority_effect'))
    need(packet['schema_version']=='lab-T14-native-mixed-adoption/v1-candidate'and packet['status']=='independently-selected-active'
        and packet['authority_effect']=='none'and packet['boundary']['operation']=='inspect-coupled-publication','explicit independently selected cold-read-only packet required')
    need(sha(compact(packet))==independent_packet_sha256,'independent cold packet differs')
    software=SelectedSoftware(modules,read_public);software.function(current_recovery_guard)
    closed(objects,('original','promotion','ingress','parent','source_selection','authority','owner_selection','trust','response_raw','native_factory','source_guard','cut_reader','permission_guard'))
    boundary=PublicationBoundary(software,objects['source_guard'],objects['cut_reader'],objects['permission_guard'],current_recovery_guard,
        packet['boundary'],independent_control_sha256=packet['boundary_sha256'],locks=locks)
    store=None;replay_store=None
    try:
        store=ReceiptStore(Path(packet['receipt_root']),tuple(packet['receipt_root_identity']),boundary)
        replay_store=ReceiptStore(Path(packet['replay_root']),tuple(packet['replay_root_identity']),boundary)
        return NativeMixedPublisher(store=store,replay_store=replay_store,boundary=boundary,original=objects['original'],promotion=objects['promotion'],ingress=objects['ingress'],
            parent=objects['parent'],source_selection=objects['source_selection'],selections=packet['selections'],identity_path=packet['identity_path'],
            identity_sha256=packet['identity_sha256'],authority=objects['authority'],owner_selection=objects['owner_selection'],trust=objects['trust'],
            response_raw=objects['response_raw'],native_store=None,native_factory=objects['native_factory'],native_selection=packet['native_selection'],
            output_roles=tuple(packet['output_roles']),extension_packages=packet['extension_packages'],mirrors=packet['mirrors'],expected_review_sha256=packet['review_sha256'])
    except BaseException:
        if replay_store is not None:replay_store.close()
        if store is not None:store.close()
        raise

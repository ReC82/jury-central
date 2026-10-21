"""Interrupteur ACTIVE/PAUSED de la génération IA par module (ticket #46,
`ModuleGenerationConfig`). Sans ligne de configuration, un module est ACTIVE (comportement
inchangé). En PAUSED, les sessions se composent uniquement depuis la banque (questions
déjà vues en dernier recours, comme lors d'une panne IA) — la correction IA n'est jamais
concernée."""

from sqlalchemy.orm import Session

from app.v1.models import ModuleGenerationConfig, ModuleGenerationStatus


def get_generation_status(db: Session, module_id: int) -> ModuleGenerationStatus:
    config = db.query(ModuleGenerationConfig).filter_by(module_id=module_id).first()
    return config.generation_status if config is not None else ModuleGenerationStatus.ACTIVE


def is_generation_paused(db: Session, module_id: int) -> bool:
    return get_generation_status(db, module_id) == ModuleGenerationStatus.PAUSED


def set_generation_status(db: Session, module_id: int, status: ModuleGenerationStatus) -> ModuleGenerationConfig:
    config = db.query(ModuleGenerationConfig).filter_by(module_id=module_id).first()
    if config is None:
        config = ModuleGenerationConfig(module_id=module_id, generation_status=status)
        db.add(config)
    else:
        config.generation_status = status
    db.flush()
    return config

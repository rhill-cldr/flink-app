from dataclasses import dataclass
from typing import Optional


@dataclass
class PostgresConf:
    path_backups: str
    db_name: str
    db_role: str
    db_pass: Optional[str]
    db_host: Optional[str]
    db_port: Optional[str]


@dataclass
class PgVectorContentConf:
    project_docs: str
    project_pdfs: Optional[str]
    cloudera_docs: Optional[str]
    cloudera_pdfs: Optional[str]
    

@dataclass
class PgVectorConf:
    sentence_transformer: str
    cross_encoder: str
    dimensions: int 
    content: PgVectorContentConf 

@dataclass
class ProjectConf:
    path_local_db: str

@dataclass
class AtkConf:
    namespace: str
    path_workspace: str
    path_tmp: Optional[str]
    project: ProjectConf
    postgres: PostgresConf
    pgvector: PgVectorConf
    defaults: dict



from sqlalchemy import (Column, DateTime, Integer,
                        Float, Text, Table, create_engine)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from databases import Database
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from fastapi_users import models
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from ..models.user import User

"""
    Add new tables here
"""


DATABASE_URL = "postgresql://postgres:intel@localhost:5432/storage_dev"


#
Base: DeclarativeMeta = declarative_base()


class UserDB(User, models.BaseUserDB):
    pass


class UserTable(Base, SQLAlchemyBaseUserTable):
    pass


engine = create_engine(DATABASE_URL)


metadata = Base.metadata
# Table creation

# memes = Table(
#     "memedb", metadata,
#     Column("id", Integer, primary_key=True),
#     Column("name", Text, nullable=False),
#     Column("url", Text, nullable=False),
#     Column("caption", Text, nullable=False),
#     Column("created_date", DateTime, index=True,
#            server_default=func.now(), nullable=False),
#     Index('uix_1', 'name', 'url', 'caption', unique=True),
#     Index('uix_2', func.lower('name'), 'created_date'))

user_states = Table(
    "user_states", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_state_type", Text, nullable=False))

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=False),
    Column("user_state_id", Integer, ForeignKey("user_states.id"),
           index=True, nullable=False),
    Column("signup_date", DateTime, server_default=func.now(),
           nullable=False))

user_space_configurations = Table(
    "user_space_configurations", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=False),
    Column("single_file_upload_limit_GB", Float, server_default="16",
           nullable=True),  # nullable=True?
    Column("total_storage_limit_GB", Float, server_default="64",
           nullable=True))  # nullable=True?

# managers = Table(
#     "managers", metadata,
#     Column("id", Integer, primary_key=True),
#     Column("user_id",  UUID(as_uuid=True), ForeignKey("user.id"),
#             nullable=False),
#     Column("joining_date", DateTime, server_default=func.now(),
#            nullable=False))

# admins = Table(
#     "admins", metadata,
#     Column("id", Integer, primary_key=True),
#     Column("user_id",  UUID(as_uuid=True), ForeignKey("user.id"),
#            index=True, nullable=False))

# user_permissions = Table(
#     "user_permissions", metadata,
#     )


# file_permissions = Table(
#     "file_permissions", metadata,
#     )

object_states = Table(
    "object_states", metadata,
    Column("id", Integer, primary_key=True),
    Column("state_type", Text, nullable=False))

object_scopes = Table(
    "object_scopes", metadata,
    Column("id", Integer, primary_key=True),
    Column("scope_type", Text, nullable=False))

folders = Table(
    "folders", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Text, nullable=False),
    Column("created_by_user",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=False),
    Column("created_on", DateTime, server_default=func.now(),
           nullable=False),
    Column("parent_directory_id", Integer, ForeignKey("folders.id"),
           index=True, nullable=True),  # is ok?
    Column("folder_state_id", Integer, ForeignKey("object_states.id"),
           index=True, nullable=False),
    Column("folder_scope_id", Integer, ForeignKey("object_scopes.id"),
           index=True, nullable=False))

folders_inactive = Table(
    "folders_inactive", metadata,
    Column("id", Integer, primary_key=True),
    Column("folder_id", Integer, ForeignKey("folders.id"),
           index=True, nullable=False),
    Column("inactive_by_user",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=False),
    Column("inactive_on", DateTime, server_default=func.now(),
           nullable=False)
    )

folders_deleted = Table(
    "folders_deleted", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Text, nullable=False),
    Column("created_by_user",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=True),  # nullable=True?
    Column("created_on", DateTime, nullable=True),  # nullable=True?
    Column("deleted_on", DateTime, server_default=func.now(),
           nullable=True),  # nullable=True?
    Column("deleted_by_user",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=True),  # nullable=True?
    Column("is_force_deleted", Boolean, nullable=False))


# file_extensions = Table(
#     "file_extensions", metadata,
#     Column("id", Integer, primary_key=True),
#     Column("file_extension", Text, nullable=False))

files = Table(
    "files", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Text, nullable=False),
    Column("uploaded_by",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=False),
    Column("uploaded_on", DateTime, server_default=func.now(),
           nullable=False),
    Column("size_in_gb", Float, nullable=True),  # nullable=True?
    Column("parent_directory_id", Integer, ForeignKey("folders.id"),
           index=True, nullable=False),
    Column("file_state_id", Integer, ForeignKey("object_states.id"),
           index=True, nullable=False),
    Column("file_scope_id", Integer, ForeignKey("object_scopes.id"),
           index=True, nullable=False))

files_starred = Table(
    "files_starred", metadata,
    Column("id", Integer, primary_key=True),
    Column("file_id", Integer, ForeignKey("files.id"),
           index=True, nullable=False),
    Column("starred_by",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=False))

files_inactive = Table(
    "files_inactive", metadata,
    Column("id", Integer, primary_key=True),
    Column("file_id", Integer, ForeignKey("files.id"),
           index=True, nullable=False),
    Column("inactive_by_user",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=False),
    Column("inactive_on", DateTime, server_default=func.now(),
           nullable=False)
    )

files_deleted = Table(
    "files_deleted", metadata,
    Column("id", Integer, primary_key=True),
    Column("file_name", Text, nullable=False),
    Column("uploaded_by_user",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=True),  # nullable=True?
    Column("uploaded_on", DateTime, nullable=True),  # nullable=True?
    Column("size_in_GB", Float, nullable=True),  # nullable=True?
    Column("deleted_on", DateTime, server_default=func.now(),
           nullable=True),  # nullable=True?
    Column("deleted_by_user",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=True),  # nullable=True?
    Column("is_force_deleted", Boolean, nullable=False))

team_states = Table(
    "team_states", metadata,
    Column("id", Integer, primary_key=True),
    Column("team_state_type", Text, nullable=False))

teams = Table(
    "teams", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Text, nullable=False),
    Column("team_state_id", Integer, ForeignKey("team_states.id"),
           index=True, nullable=False),
    Column("single_file_upload_limit_GB", Float,
           default=16, nullable=True),  # nullable=True?
    Column("total_storage_limit_GB", Float, default=128,
           nullable=True),  # nullable=True?
    Column("created_on", DateTime, server_default=func.now(),
           nullable=False))

team_member_roles = Table(
    "team_member_roles", metadata,
    Column("id", Integer, primary_key=True),
    Column("role", Text, nullable=False))

team_members = Table(
    "team_members", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=False),
    Column("team_id", Integer, ForeignKey("teams.id"),
           index=True, nullable=False),
    Column("role_id", Integer, ForeignKey("team_member_roles.id"),
           index=True, nullable=False),
    Column("joining_date", DateTime, server_default=func.now(),
           nullable=False),
    Column("is_member_active", Boolean, nullable=False))

team_object_states = Table(
    "team_object_states", metadata,
    Column("id", Integer, primary_key=True),
    Column("state_type", Text, nullable=False))

team_object_scopes = Table(
    "team_object_scopes", metadata,
    Column("id", Integer, primary_key=True),
    Column("scope_type", Text, nullable=False))

team_folders = Table(
    "team_folders", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Text, nullable=False),
    Column("team_id", Integer, ForeignKey("teams.id"),
           index=True, nullable=False),
    Column("created_by_user",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=False),
    Column("created_on", DateTime, server_default=func.now(),
           nullable=False),
    Column("parent_directory_id", Integer, ForeignKey("team_folders.id"),
           index=True, nullable=True),  # is ok?
    Column("folder_state_id", Integer, ForeignKey("team_object_states.id"),
           index=True, nullable=False),
    Column("folder_scope_id", Integer, ForeignKey("team_object_scopes.id"),
           index=True, nullable=False))

team_folders_inactive = Table(
    "team_folders_inactive", metadata,
    Column("id", Integer, primary_key=True),
    Column("team_folder_id", Integer, ForeignKey("team_folders.id"),
           index=True, nullable=False),
    Column("inactive_by_user",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=False),
    Column("inactive_on", DateTime, server_default=func.now(),
           nullable=False)
    )

team_folders_deleted = Table(  # program and see
    "team_folders_deleted", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Text, nullable=False),
    Column("team_id", Integer, ForeignKey("teams.id"),
           index=True, nullable=False),
    Column("created_by_user",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=True),  # nullable=True?
    Column("created_on", DateTime, nullable=True),  # nullable=True?
    Column("deleted_on", DateTime, server_default=func.now(),
           nullable=True),  # nullable=True?
    Column("deleted_by_user",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=True),  # nullable=True?
    Column("is_force_deleted", Boolean, nullable=False))

team_files = Table(
    "team_files", metadata,
    Column("id", Integer, primary_key=True),
    Column("team_id", Integer, ForeignKey("teams.id"),
           index=True, nullable=False),
    Column("name", Text, nullable=False),
    Column("uploaded_by",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=False),
    Column("uploaded_on", DateTime, server_default=func.now(),
           nullable=False),
    Column("size_in_GB", Float, nullable=True),  # nullable=True?
    Column("parent_directory_id", Integer, ForeignKey("team_folders.id"),
           index=True, nullable=False),
    Column("file_state_id", Integer, ForeignKey("team_object_states.id"),
           index=True, nullable=False),
    Column("file_scope_id", Integer, ForeignKey("team_object_scopes.id"),
           index=True, nullable=False))

team_files_starred = Table(
    "team_files_starred", metadata,
    Column("id", Integer, primary_key=True),
    Column("team_file_id", Integer, ForeignKey("team_files.id"),
           index=True, nullable=False),
    Column("starred_by",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=False))

team_files_inactive = Table(
    "team_files_inactive", metadata,
    Column("id", Integer, primary_key=True),
    Column("team_file_id", Integer, ForeignKey("team_files.id"),
           index=True, nullable=False),
    Column("inactive_by_user",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=False),
    Column("inactive_on", DateTime, server_default=func.now(),
           nullable=False)
    )

team_files_deleted = Table(  # program and see
    "team_files_deleted", metadata,
    Column("id", Integer, primary_key=True),
    Column("team_id", Integer, ForeignKey("teams.id"),
           index=True, nullable=False),
    Column("file_name", Text, nullable=False),
    Column("uploaded_by_user",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=True),  # nullable=True?
    Column("uploaded_on", DateTime, nullable=True),  # nullable=True?
    Column("size_in_GB", Float, nullable=True),  # nullable=True?
    Column("deleted_on", DateTime, server_default=func.now(),
           nullable=True),  # nullable=True?
    Column("deleted_by_user",  UUID(as_uuid=True), ForeignKey("user.id"),
           index=True, nullable=True),  # nullable=True?
    Column("is_force_deleted", Boolean, nullable=False))


aws_files = Table(
     "aws_files", metadata,
     Column("id", Integer, primary_key=True),
     Column("file_id", Integer, ForeignKey("files.id"),
            index=True, nullable=False),
     Column("aws_file_name", Text, unique=True, nullable=False),
     )

aws_team_files = Table(
     "aws_team_files", metadata,
     Column("id", Integer, primary_key=True),
     Column("file_id", Integer, ForeignKey("team_files.id"),
            index=True, nullable=False),
     Column("aws_file_name", Text, unique=True, nullable=False),
     )

# share_links = Table(
#     "share_links", metadata,
#     )

# make login-logout logs for users and admin

# databases query builder
database = Database(DATABASE_URL)
users = UserTable.__table__
user_db = SQLAlchemyUserDatabase(UserDB, database, users)

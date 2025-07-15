from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import pyckson
from pyckson.dates.arrow import ArrowStringFormatter

pyckson.configure_explicit_nulls(use_explicit_nulls=True)

@dataclass
class StorageObject(object):
    """Storage object information (only in empty folder messages)"""
    storage_object_id: int
    type: str
    name: str
    project_id: int
    orig_storage_object_id: int
    content_change_storage_object_id: int
    storage_object_path_id: int
    created: int
    modified: int
    hash: Optional[str]
    revision: Optional[str]
    file_service_id: Optional[str]
    flag: Optional[str]

    

@dataclass
class FolderDeleteInput(object):
    folder_id: str
    activity_id: str

@dataclass
class FolderDeleteError(object):
    code: Optional[str] = None
    message: Optional[str] = None

@dataclass
class FolderDeleteResult(object):
    download_url: Optional[str] = None
    object_to_delete: Optional[StorageObject] = None
    object_deleted: Optional[StorageObject] = None
    type: Optional[str] = None
    parent_storage_object_id: Optional[int] = None
    error: Optional[FolderDeleteError] = None

@dataclass
class UserInput(object):
    id: str
    tiduuid : str

@dataclass
@pyckson.date_formatter(ArrowStringFormatter())
class FolderDeleteQueueMessage(object):
    """A class that represents the message sent as part of the input event."""
    created_by: UserInput
    input: FolderDeleteInput
    job_id: Optional[str] = None
    job_type: Optional[str] = None
    status: Optional[str] = None
    project_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    result: Optional[FolderDeleteResult] = None
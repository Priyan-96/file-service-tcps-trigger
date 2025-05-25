"""This module consists of the classes that matches the event message published by File Service."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

import pyckson
from pyckson.dates.arrow import ArrowStringFormatter

pyckson.set_defaults(pyckson.explicit_nulls)


@dataclass(frozen=True)
class FileOrFolderData(object):
    """This class represents the object(FILE or FOLDER) data."""
    # object identifier (tc visible id)
    id: str
    # object version identifier
    version_id: str
    # object type
    type: str
    # object parent identifier (tc visible id)
    parent_id: str
    # object type of parent
    parent_type: str
    # object project identifier (tc visible id)
    project_id: str
    # activity identifier (tc visible id)
    activity_id: str
    # client name like my.sketchup
    client_name: Optional[str]
    # size of the uploaded file
    file_size: Optional[int]
    # ecom transaction id
    ecom_transaction_id: Optional[str]
    # entitlement id
    entitlement_id: Optional[str]
    # processing priority - NA, LOW, HIGH
    processing_priority: Optional[str]
    # old_parent_id
    old_parent_id: Optional[str]
    # old name
    old_name: Optional[str]
    # move rename activity id
    move_rename_activity_id: Optional[str]
    # old version id
    old_version_id: Optional[str]
    # tcfs space id
    tcfs_space_id: Optional[str]
    # tcfs file id
    tcfs_file_id: Optional[str]
    # tcfs version id
    tcfs_version_id: Optional[str]



@dataclass(frozen=True)
class UserIdentity(object):
    """A class to represent user identity."""
    # user identifier (tc visible id)
    id: str
    # tid uuid of the user
    tiduuid: str


@dataclass(frozen=True)
class FileFolderPermissionEventData:
    """Represents file or folder permission event data."""
    file_id: Optional[str]
    folder_id: Optional[str]
    project_id: str
    newly_added_permissions: List[str]
    updated_permissions: List[str]
    removed_permissions: List[str]

@dataclass(frozen=True)
@pyckson.date_formatter(ArrowStringFormatter())
class FileOrFolderEvent(object):
    """A class to represent file or folder event."""
    # event type like FILE_ADD, FILE_UPDATE ...
    event_type: str
    # event time in iso format
    event_time: datetime
    user_identity: UserIdentity
    # identifier to correlate logs between services
    correlation_id: str
    # event version identifier
    event_version: str
    object_data: Optional[FileOrFolderData] = None
    # file or folder permission event data
    file_permission_event_data: Optional[FileFolderPermissionEventData] = None
    file_folder_permission_event_data: Optional[FileFolderPermissionEventData] = None
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import pyckson
from pyckson.dates.arrow import ArrowStringFormatter

pyckson.configure_explicit_nulls(use_explicit_nulls=True)

@dataclass
class FolderDeleteInput(object):
    f_id: str
    a_id: str

@dataclass
class FolderDeleteError(object):
    code: Optional[str] = None
    message: Optional[str] = None

@dataclass
class FolderDeleteResult(object):
    download_url: Optional[str] = None
    error: Optional[FolderDeleteError] = None

@dataclass
class UserInput(object):
    id: str
    tiduuid : str

@dataclass
@pyckson.date_formatter(ArrowStringFormatter())
class FolderDeleteQueueMessage(object):
    """A class that represents the message sent as part of the input event."""
    job_id: str
    job_type: str
    status: str
    project_id: str
    created_by: UserInput
    created_at: datetime
    updated_at: datetime
    input: FolderDeleteInput
    result: Optional[FolderDeleteResult] = None
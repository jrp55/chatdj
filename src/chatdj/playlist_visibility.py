from enum import Enum, auto


class PlaylistVisibility(Enum):
    Private = auto()
    Public = auto()

    @classmethod
    def from_str(cls, s: str):
        if s == 'Private':
            return cls.Private
        elif s == 'Public':
            return cls.Public

        raise RuntimeError(f'Cannot parse {s} into PlaylistVisibility')

    def to_str(self) -> str:
        if self == PlaylistVisibility.Private:
            return 'Private'
        else:
            return 'Public'

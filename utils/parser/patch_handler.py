from abc import ABC, abstractmethod


class PatchHandler(ABC):
    @abstractmethod
    def prepare_patch(self, rom_file, directory_patch, patch) -> str:
        pass
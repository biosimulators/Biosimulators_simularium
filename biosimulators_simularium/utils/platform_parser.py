import os
from abc import ABC, abstractmethod
import platform
import subprocess as sp


class OSPlatform:
    def __init__(self):
        self.value = platform.platform()


class PlatformParser(ABC):
    def __init__(self):
        self.plat = OSPlatform()
        
    @abstractmethod
    def _scan(self) -> str:
        pass 
    
    @abstractmethod
    def _assert_platform(self, plat) -> bool:
        pass 
    
    @abstractmethod
    def _install_dep(self, dep) -> None:
        pass 
    
    
class SmoldynPlatformParser(PlatformParser):
    def __init__(self):
        super().__init__()
        self._install_dep()

    def _scan(self):
        return self.plat.value

    def _assert_platform(self, plat) -> bool:
        this_platform = self._scan()
        return plat in this_platform

    def _install_dep(self, dep: str = 'smoldyn'):
        is_mac = self._assert_platform('mac')
        if not is_mac:
            sp.run(f"pip install {dep}".split(), capture_output=True, shell=True, text=True)
        else:
            smoldyn_install_dirpath = '.smoldyn-2.72-mac'
            result = sp.run('sudo -H ./install.sh'.split(), cwd=smoldyn_install_dirpath)
            try:
                print('Installation successful!')
            except result.returncode == 0:
                print('Installation failed!')

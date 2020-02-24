#!/usr/bin/python3

import sys
import os
import pytest
import pdb
from httpobs.scanner.local import scan


try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print ('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')

from zbConfig import defaultEnv
from zbMozillaOb import MozillaObs



class Test_Observ:
    @pytest.mark.parametrize("testList", ['testing.zingbox.com', 'enterprise.zingbox.com'])

    def test_observ(self,testList):
        assert MozillaObs.scanHost(testList) == True

import functools
import pytest
class Test_01():
    def decorator_example(fn):

        @functools.wraps(fn)
        def create(*args, **kwargs):
            # any code here
            return fn(*args, **kwargs)
        return create

    @pytest.mark.parametrize("test_params",[1,2])
    @decorator_example
    def test_1(self,test_params):
        pass

if __name__ =="__main__":
    pytest.main(["-v","./test_11.py"])
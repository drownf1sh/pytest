import pytest

# @pytest.mark.test001
class Test01:

    @pytest.mark.parametrize('num',['qwe','13we','123edwef','ui.j'])

    def test_two(self,num):
        if 'ui' in num:
            pytest.skip()
        print(num)
        assert 4 == 4

if __name__ == "__main__":
    # 若存在多个标记，则用or连接，形成一个测试集，比如'-m=assetList or test or allLists'
    pytest.main(['-v', 'case01.py', "--html=./log/123.html"])
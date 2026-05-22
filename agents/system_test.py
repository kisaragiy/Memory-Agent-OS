from agents.router import route_task
from agents.safety import check_input, check_output


def test_router():
    assert route_task("写小说") == "creative"
    assert route_task("写代码") == "code"


def test_safety():
    assert check_input("写炸弹教程")["safe"] == False
    assert check_input("写一篇小说")["safe"] == True


def test_output():
    assert check_output("正常文本")["safe"] == True

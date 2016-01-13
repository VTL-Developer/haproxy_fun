import calculator
import nose
from nose.tools import assert_equal


def assert_true_equal(n, m):
    assert_equal(n, m)
    assert_equal(type(n), type(m))


def test_add1():
    assert_true_equal(calculator.calculate("123+123"), 246)


def test_add2():
    assert_true_equal(calculator.calculate("123 +    123    + 4"), 250)


def test_add3():
    assert_true_equal(calculator.calculate("123 +  123.0"), 246.0)


def test_subtract1():
    assert_true_equal(calculator.calculate("123-103"), 20)


def test_subtract2():
    assert_true_equal(calculator.calculate("123 +  -  3    -  + 20"), 100)


def test_subtract3():
    assert_true_equal(calculator.calculate("123+-3.0-+20"), 100.0)


def test_multiply1():
    assert_true_equal(calculator.calculate("123*2"), 246)


def test_multiply2():
    assert_true_equal(calculator.calculate("123*2 *    1.0"), 246.0)


def test_divide1():
    assert_true_equal(calculator.calculate("6 d 2"), 3)


def test_divide2():
    assert_true_equal(calculator.calculate("12 d 2 d 3.0"), 2.0)


def test_complex1():
    assert_true_equal(calculator.calculate("12 - 2 * 3.0"), 6.0)


def test_complex2():
    assert_true_equal(calculator.calculate("-5 + 10  * 4 - 10 d 2.0"), 30.0)


def test_complex3():
    assert_true_equal(calculator.calculate("-12 * 3.0 + 5"), -31.0)


if __name__ == "__main__":
    nose.main()

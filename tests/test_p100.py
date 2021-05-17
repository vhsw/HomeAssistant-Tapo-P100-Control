from tapo_p100_control.p100 import sha1


def test_sha_digest():
    assert sha1("user") == "12dea96fec20593566ab75692c9949596833adc9"

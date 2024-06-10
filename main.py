import match_conpot
import match_dionaea
import sys


def main(ip):
    conpot_result = match_conpot.main(ip)
    dionaea_result = match_dionaea.main(ip)
    # print(dionaea_result)
    print(f"Conpot fingerprinting match: {conpot_result.count(True)}"
          + f"/{len(conpot_result)}")
    print(f"Dionaea fingerprinting match: {dionaea_result.count(True)}"
          + f"/{len(dionaea_result)}")

    conpot_score = conpot_result.count(True) / len(conpot_result)
    dionaea_score = dionaea_result.count(True) / len(dionaea_result)
    if conpot_score == 1:
        print(f"{ip} is likely a Conpot honeypot.")
    elif dionaea_score == 1:
        print(f"{ip} is likely a Dionaea honeypot.")
    else:
        print(f"{ip} is not a honeypot.")


if __name__ == '__main__':
    ip = '127.0.0.1'
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    main(ip)

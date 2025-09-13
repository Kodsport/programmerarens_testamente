def generateFile(flag: str):
    import base64
    return f'''# indata är en lista
import base64
sal = base64.b64decode({base64.b64encode(flag.encode())}).decode()

def kollaOmRätt(funktion):
    from io import StringIO 
    import sys

    class Capturing(list):
        def __enter__(self):
            self._stdout = sys.stdout
            sys.stdout = self._stringio = StringIO()
            return self
        def __exit__(self, *args):
            self.extend(self._stringio.getvalue().splitlines())
            del self._stringio
            sys.stdout = self._stdout

    for i in range(10):
        import random
        ls = sorted([random.randint(1_000, 1_000_000) for i in range(random.randint(10, 20))])
        i, j = random.sample(range(len(ls)), 2)
        target = ls[i] + ls[j]
        with Capturing() as output:
            funktion([ls, target])
        i,j = map(int,output[0].split())
        if ls[i]+ls[j] != target:
            print(f'Tyvärr! Ni svarade position {{i}} och {{j}} vilket motsvarar {{ls[i]}}+{{ls[j]}}={{ls[i]+ls[j]}}')
            break
    else:
        print(f'Sal {{sal}}')
'''.replace('{{{{rumsnummer}}}}', flag)

################################################################################

if __name__ == '__main__':
    import importlib.util
    import sys

    module_name = 'template'
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    template = importlib.util.module_from_spec(spec)

    exec(generateFile('rumsnummer'), template.__dict__)

    sys.modules[module_name] = template

################################################################################

    import template

    def minFunk(indata):
        ls = indata[0]
        target = indata[1]
        lp = 0
        rp = len(ls)-1
        while (lp <= rp):
            if ls[lp] + ls[rp] > target:
                rp -= 1
            elif ls[lp] + ls[rp] < target:
                lp += 1
            elif ls[lp] + ls[rp] == target:
                break
        print(lp, rp)
    template.kollaOmRätt(minFunk)

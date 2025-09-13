def generateFile(flag: str):
    import base64
    return f'''Du får tre hörn av en rektangel och du vill hitta det sista hörnet. indata är en lista bestående av tre listor med två koordinater i varje:
en x-koordinat och en y-koordinat. Alltså typ [[0,0], [1,0], [0,1]] och då ska du skriva ut print(1,1)
    
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
        x1, x2 = sorted(random.sample(range(-100, 101), 2))
        y1, y2 = sorted(random.sample(range(-100, 101), 2))
        rect = [[x1,y1], [x1,y2], [x2,y1]]
        random.shuffle(rect)
        with Capturing() as output:
            funktion(rect)
        i,j = map(int,output[0].split())
        if (i,j) != (x2, y2):
            print(f'Tyvärr! För rektangeln {{rect}} svarade ni {{i,j}}, men svaret var {{x2,y2}}')
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
        x = indata[0][0] ^ indata[1][0] ^ indata[2][0]
        y = indata[0][1] ^ indata[1][1] ^ indata[2][1]
        print(x, y)

    template.kollaOmRätt(minFunk)

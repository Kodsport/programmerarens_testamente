def generateFile(flag: str):
    import base64
    return f'''import base64
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
        with Capturing() as output:
            funktion('python')
        if output != ['hej python']:
            print(f'Tyvärr! {{output}}')
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
        print(f'hej {indata}')

    template.kollaOmRätt(minFunk)

import base64
sal = base64.b64decode(b'{{{{rumsnummer}}}}').decode()

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
            print(f'Tyvärr! {output}')
            break
    else:
        print(f'Sal {sal}')

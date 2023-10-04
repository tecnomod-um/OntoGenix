from REPL.REPL import PythonREPL

class KGen:

    def __init__(self, dataset, destination):
        self.dataset = dataset
        self.destination = destination

        code = '''
        import morph_kgc
        graph = morph_kgc.materialize({dataset})
        graph.serialize(destination={destination}, format='ntriples', endoding="utf-8")
        '''

    def run(self):
        try:
            code.format(dataset=self.dataset, destination=self.destination)
            output =  PythonREPL().run(code)
            return output
        except Exception:
            print('Error in KGen')
 
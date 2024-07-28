"""
$ python test_group.py
NAME
    test_group.py

SYNOPSIS
    test_group.py GROUP | COMMAND

GROUPS
    GROUP is one of the following:

     digestion

     ingestion


$ python test_group.py digestion
NAME
    test_group.py digestion

SYNOPSIS
    test_group.py digestion COMMAND

COMMANDS
    COMMAND is one of the following:

     run

     status


$ python test_group.py run
Ingesting! Nom nom nom...
Burp!

$ python test_group.py ingestion run
Ingesting! Nom nom nom...

$ python test_group.py digestion run
Burp!

$ python test_group.py digestion status
Satiated.

"""

import fire


class IngestionStage:

    def run(self):
        return 'Ingesting! Nom nom nom...'


class DigestionStage:

    def run(self, volume=1):
        return ' '.join(['Burp!'] * volume)

    def status(self):
        return 'Satiated.'


class Pipeline:

    def __init__(self):
        self.ingestion = IngestionStage()
        self.digestion = DigestionStage()

    def run(self):
        ingestion_output = self.ingestion.run()
        digestion_output = self.digestion.run()
        return [ingestion_output, digestion_output]


if __name__ == '__main__':
    fire.Fire(Pipeline)

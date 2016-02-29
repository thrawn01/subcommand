
Complete documentation is available [here](http://subcommand.org)

# SubCommand CLI Parser

SubCommand is a simple and concise SubCommand parser to assist CLI developers
in creating relatively complex sub commands.

The SubCommand project fits into a single file, which is less than 500 lines.
The interface consists of 3 Classes and a few decorators and that is it.

**Doesn't argparse already support sub commands?**

I does, but in practice it can be quite complex and it makes keeping the args
and the subcommands together and easily reasoned about difficult in large CLI
code bases.

**Doesn't project X already do this?**

There are several projects that attempt to solve the sub command problem.

* *Plumbum* - http://plumbum.readthedocs.org/en/latest/cli.html
* *Click* - http://click.pocoo.org
* *Cliff* - http://docs.openstack.org/developer/cliff

When I originally wrote `SubCommand` none of these projects existed, and even
now none of them are as small and simple to use as SubCommand. IMHO =)

In fact `SubCommand` is so small you can easily copy single .py module into your
own project to avoid carrying around yet another external dependency.

## Installation

Install via pip
```
$ pip install cli-subcommand
```

## What does it look like?

Here is simple example
``` python
from subcommand import opt, noargs
import subcommand
import sys

class TestCommands(subcommand.Commands):

    def __init__(self):
        subcommand.Commands.__init__(self)
        self.opt('-d', '--debug', action='store_const',
                 const=True, default=False, help="Output debug")
        self.count = 0

    @opt('--count', default=1, type=int, help="Num of Hello's")
    @opt('name', help="Your name")
    def hello(self, name, count=1):
        """ Docstring for hello """
        for x in range(count):
            print('Hello, %s' % name)
            self.count += 1
        return 0

    @noargs
    def return_non_zero(self):
        if self.debug:
            print('Exit with non-zero status')
        return 1

if __name__ == "__main__":
    parser = subcommand.Parser([TestCommands()],
                               desc='Test Application')
    sys.exit(parser.run())
```

It looks like this when run
```
    $ python hello.py hello derrick --count 5
    Hello, derrick
    Hello, derrick
    Hello, derrick
    Hello, derrick
    Hello, derrick
    $ echo $?
```
What it looks like when you pass no arguments
```
    $ python hello.py
    Usage: hello.py <command> [-h]

    Test Application

    Available Commands:
       return-non-zero
       hello
```
What it looks like when you ask for `hello -h`
```
    $ python hello.py hello -h
    usage: hello [-h] [--count COUNT] [-d] name

    Docstring for hello

    positional arguments:
      name           Your name

    optional arguments:
      -h, --help     show this help message and exit
      --count COUNT  Num of Hello's
      -d, --debug    Output debug
```

## Can my commands have subcommands?
In order to use subcommands you must use the **subcommand.SubParser** class to
parse your **subcommand.Commands** objects. In addition you must give your
**Commands** object a name by giving it the **_name** attribute.

Example
```python
    from subcommand import opt, noargs
    import subcommand
    import sys

    class BaseCommands(subcommand.Commands):
        def pre_command(self):
            self.client = self.client_factory()

    class TicketCommands(BaseCommands):
        """ Ticket SubCommand Docs """
        _name = 'tickets'
        @opt('tkt-num', help="tkt number to get")
        def get(self, tkt_num):
            """ Get Ticket docstring """
            print(self.client.get_ticket(tkt_num))

    class QueueCommands(BaseCommands):
        """ Queue SubCommand Docs """
        _name = 'queues'
        @opt('queue-num', help="queue to get")
        def get(self, queue_num):
            print(self.client.get_queue(queue_num))

    if __name__ == "__main__":
        parser = subcommand.SubParser([TicketCommands(),
                                       QueueCommands()],
                                      desc='Ticket Client')
        sys.exit(parser.run())
```

What it looks like when you run it
```
    $ python hello.py
    Usage: hello.py <command> [-h]

    Ticket Client

    Available Commands:
       tickets
       queues
```

When you run the subcommands
```
    $ python hello.py tickets
    Usage: hello.py tickets <command> [-h]

    Ticket SubCommand Docs

    Available Commands:
       get
```

Getting help from the sub command
```
    $ python hello.py tickets get -h
    usage: get [-h] tkt-num

    Get Ticket docstring

    positional arguments:
      tkt-num     tkt number to get

    optional arguments:
      -h, --help  show this help message and exit
```

## API Documentation

Complete documentation is available [here](http://thrawn01.org/subcommand)


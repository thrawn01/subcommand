.. _index:


SubCommand CLI Parser
======================

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


Installation
-----------------------

Install via pip::

    $ pip install cli-subcommand

Source is available here http://github.com/thrawn01/subcommand


What does it look like?
-----------------------

Here is simple example::

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

It looks like this when run::

    $ python hello.py hello derrick --count 5
    Hello, derrick
    Hello, derrick
    Hello, derrick
    Hello, derrick
    Hello, derrick
    $ echo $?

What it looks like when you pass no arguments::

    $ python hello.py
    Usage: hello.py <command> [-h]

    Test Application

    Available Commands:
       return-non-zero
       hello

What it looks like when you ask for `hello -h`::

    $ python hello.py hello -h
    usage: hello [-h] [--count COUNT] [-d] name

    Docstring for hello

    positional arguments:
      name           Your name

    optional arguments:
      -h, --help     show this help message and exit
      --count COUNT  Num of Hello's
      -d, --debug    Output debug


Can my commands have subcommands?
---------------------------------
In order to use subcommands you must use the
:class:`subcommand.SubParser<subcommand.SubParser>` Class to parse your
:class:`subcommand.Commands<subcommand.Commands>` objects. In addition you must
give your `Commands` object a name by giving it the **_name** attribute.

Example::

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


What it looks like when you run it::

    $ python hello.py
    Usage: hello.py <command> [-h]

    Ticket Client

    Available Commands:
       tickets
       queues

When you run the subcommands::

    $ python hello.py tickets
    Usage: hello.py tickets <command> [-h]

    Ticket SubCommand Docs

    Available Commands:
       get

Getting help from the sub command::

    $ python hello.py tickets get -h
    usage: get [-h] tkt-num

    Get Ticket docstring

    positional arguments:
      tkt-num     tkt number to get

    optional arguments:
      -h, --help  show this help message and exit

What if I have lots of arguments?
---------------------------------
If you have a command with a ton of command line arguments, and don't really
want to specify each in the method signature you can specify a single argument
called **args** and SubCommand will detect this and pass in all the arguments
as a list.

Here is an example of a CLI interface to a ticketing system::

    class TicketCommands(Commands):
        def __init__(self):
            SubCommand.__init__(self)
            # Add debug option to all commands (creates self.debug)
            self.opt('-d', '--debug', action='store_const',
                     const=True, default=False,
                     help="print server requests and responses")
            self.opt('-U', '--url', default=None,
                     help="URL to our ticketing rest api")

        @opt('-c', '--classification', type=int,
             help="Specify the class of this ticket")
        @opt('text', help="Body of the ticket")
        @opt('subject', help="Subject of the ticket")
        @opt('severity', type=int, help="Tkt severity level")
        @opt('subcategory', help="The subcategory")
        @opt('queue-name', help="Name of the queue")
        def add_ticket(self, args):
            client = self.ticket_factory()
            # Remove --url and --debug
            args = self.remove(args, ['url', 'debug'])
            # The ticket client requires some args to
            # be optional so we split them here
            args, kwargs = self.split(args, ['queue_name',
                    'subcategory', 'source', 'severity',
                    'subject', 'text'])
            resp = client.add_ticket(args['queue_name'],
                                     args['subcategory'],
                                     args['source'],
                                     args['severity'],
                                     args['subject'],
                                     args['text'], **kwargs)
            print(resp.to_json())


Can I share options amongst similar commands?
---------------------------------------------
Global options can be specified within the constructor by using the
:meth:`subcommand.Commands.opt<subcommand.Commands.opt>` method, and then accessed via **self**

In our ticket client example above here is how to share the --debug and --url options::

    class TicketCommands(Commands):
        def __init__(self):
            SubCommand.__init__(self)
            # Add debug option to all commands (creates self.debug)
            self.opt('-d', '--debug', action='store_const',
                     const=True, default=False,
                     help="print server requests and responses")
            self.opt('-U', '--url', default=None,
                     help="URL to our ticketing rest api")

        @noargs
        def ticket_cmd1(self):
            print("called ticket_cmd1")
            print(self.debug)
            print(self.url)

        @noargs
        def ticket_cmd2(self):
            print("called ticket_cmd2")
            print(self.debug)
            print(self.url)


Can I execute common code before each command?
----------------------------------------------
You can define a pre_command method which will get executed before a command is run

To further our ticket example::

    class TicketCommands(Commands):
        def pre_command(self):
            self.client = ticket.client_factory()

        @opt('tkt-num', help="tkt number to get")
        def get_ticket(self, tkt_num):
            print(self.client.get_ticket(tkt_num))

        @opt('tkt-num', help="tkt number to delete")
        def delete_ticket(self):
            print(self.client.delete_ticket(tkt_num))


Does SubCommand provide bash completion?
-----------------------------------------
Once you have created your CLI with SubCommand you can generate a bash
completion script on ubuntu by running the following::

    ./my-script.py --bash-completion-script > /etc/bash_completion.d/my-script.py


Installation
============

This part of the documentation covers the installation of SubCommand.
The first step to using any software package is getting it properly installed.


Distribute & Pip
----------------

Installing SubCommand is simple with `pip <https://pip.pypa.io>`_, just run
this in your terminal::

    $ pip install git+https://github.com/thrawn01/subcommand.git

Get the Code
------------

SubCommand is developed on GitHub, You can find the code
`here <https://github.com/thrawn01/subcommand>`_.

Clone the public repository::

    $ git clone git://github.com/thrawn01/subcommand.git


Once you have a copy of the source, you can embed it in your Python package,
or install it into your site-packages easily::

    $ python setup.py install


Developer Interface
===================

.. module:: subcommand

This part of the documentation covers all the interfaces of SubCommand.

Decorators
--------------

:class:`Commands<Commands>` Methods decorated with these functions indicate the
method is a command and should be exposed via the command line.

.. autofunction:: opt
.. autofunction:: noargs


Commands Class
---------------

Use this class to define the sub commands to be exposed via the command line.

.. autoclass:: subcommand.Commands
   :inherited-members:

Parser Class
---------------

.. autoclass:: subcommand.Parser
   :inherited-members:

SubParser Class
---------------

.. autoclass:: subcommand.SubParser
   :inherited-members:



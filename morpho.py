#!/usr/bin/env python

#
# morpho.py
#
# author: j.n. kofron <jared.kofron@gmail.com>
#
from pystan import stan
import pystanLoad as pyL
from h5py import File as HDF5
from yaml import load as yload
from argparse import ArgumentParser
from inspect import getargspec


class stan_args(object):
    def read_param(self, yaml_data, node, default):
        data = yaml_data
        xpath = node.split('.')
        try:
            for path in xpath:
                data = data[path]
        except Exception as exc:
            if default == 'required':
                err = """FATAL: Configuration parameter {0} required but not\
                provided in config file!
                """.format(node)
                print(err)
                raise exc
            else:
                data = default
        return data

    def gen_arg_dict(self):
        d = self.__dict__
        sca = getargspec(pyL.stan_cache)
        sa = getargspec(stan)
        return {k: d[k] for k in (sa.args + sca.args) if k in d}

    def __init__(self, yd):
        try:
            # STAN model stuff
            self.model_code = self.read_param(yd, 'stan.model.file', 'required')
            self.cashe_dir = self.read_param(yd, 'stan.model.cache', './cache')

            # STAN data
            datafiles = self.read_param(yd, 'stan.data', 'required')
            self.data = pyL.stan_data_files(datafiles)

            # STAN run conditions
            self.algorithm = self.read_param(yd, 'stan.run.algorithm', 'NUTS')
            self.iter = self.read_param(yd, 'stan.run.iter', 2000)
            self.warmup = self.read_param(yd, 'stan.run.warmup', self.iter/2)
            self.chains = self.read_param(yd, 'stan.run.chains', 4)
            self.thin = self.read_param(yd, 'stan.run.thin', 1)
            self.init = self.read_param(yd, 'stan.run.init', '')

            # output information
            self.out_format = self.read_param(yd, 'stan.output.format', 'hdf5')
            self.out_fname = self.read_param(yd, 'stan.output.name',
                                                 'stan_out.h5')
            self.out_cfg = self.read_param(yd, 'stan.output.config', None)
            self.out_vars = self.read_param(yd, 'stan.output.data', None)
        except Exception as err:
            raise err


def parse_args():
    '''
    Parse the command line arguments provided to morpho.
    '''
    p = ArgumentParser(description='''
        An analysis tool for Project 8 data.
    ''')
    p.add_argument('--config',
                   metavar='<configuration file>',
                   help='Full path to the configuration file used by morpho',
                   required=True)
    return p.parse_args()


def open_or_create(hdf5obj, groupname):
    """
    Create a group within an hdf5 object if it doesn't already exist,
    and return the resulting group.
    """
    if groupname != "/" and groupname not in hdf5obj.keys():
        hdf5obj.create_group(groupname)
    return hdf5obj[groupname]


def write_result_hdf5(conf, stanres):
    """
    Write the STAN result to an HDF5 file.
    """
    with HDF5(conf.out_fname) as ofile:
        g = open_or_create(ofile, conf.out_cfg['group'])
        fit = stanres.extract()
        for var in conf.out_vars:
            stan_parname = var['stan_parameter']
            if stan_parname not in fit:
                warning = """WARNING: data {0} not found in fit!  Skipping...
                """.format(stan_parname)
                print warning
            else:
                g[var['output_name']] = fit[stan_parname]


if __name__ == '__main__':
    args = parse_args()
    with open(args.config, 'r') as cfile:
        try:
            cdata = yload(cfile)
            sa = stan_args(cdata)
            result = pyL.stan_cache(**(sa.gen_arg_dict()))

            if sa.out_format == 'hdf5':
                write_result_hdf5(sa, result)

        except Exception as err:
            print(err)
from pypy.interpreter.mixedmodule import MixedModule

class Module(MixedModule):
    appleveldefs = {
    }

    interpleveldefs = {
        'set_param':    'interp_jit.set_param',
        'residual_call': 'interp_jit.residual_call',
        'not_from_assembler': 'interp_jit.W_NotFromAssembler',
        'get_jitcell_at_key': 'interp_jit.get_jitcell_at_key',
        'dont_trace_here': 'interp_jit.dont_trace_here',
        'trace_next_iteration': 'interp_jit.trace_next_iteration',
        'trace_next_iteration_hash': 'interp_jit.trace_next_iteration_hash',
        'set_compile_hook': 'interp_resop.set_compile_hook',
        'set_abort_hook': 'interp_resop.set_abort_hook',
        'get_stats_snapshot': 'interp_resop.get_stats_snapshot',
        'enable_debug': 'interp_resop.enable_debug',
        'disable_debug': 'interp_resop.disable_debug',
        'ResOperation': 'interp_resop.WrappedOp',
        'DebugMergePoint': 'interp_resop.DebugMergePoint',
        'JitLoopInfo': 'interp_resop.W_JitLoopInfo',
        'PARAMETER_DOCS': 'space.wrap(rpython.rlib.jit.PARAMETER_DOCS)',
    }

    def setup_after_space_initialization(self):
        # force the __extend__ hacks to occur early
        from pypy.module.pypyjit.interp_jit import pypyjitdriver
        from pypy.module.pypyjit.hooks import pypy_hooks
        # add the 'defaults' attribute
        from rpython.rlib.jit import PARAMETERS
        space = self.space
        pypyjitdriver.space = space
        w_obj = space.wrap(PARAMETERS)
        space.setattr(space.wrap(self), space.wrap('defaults'), w_obj)
        pypy_hooks.space = space

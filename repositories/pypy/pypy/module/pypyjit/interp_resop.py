
from pypy.interpreter.typedef import (TypeDef, GetSetProperty,
     interp_attrproperty, interp_attrproperty_w)
from pypy.interpreter.baseobjspace import W_Root
from pypy.interpreter.gateway import unwrap_spec, interp2app
from pypy.interpreter.pycode import PyCode
from pypy.interpreter.error import OperationError
from rpython.rtyper.lltypesystem import lltype
from rpython.rtyper.annlowlevel import cast_base_ptr_to_instance, hlstr
from rpython.rtyper.rclass import OBJECT
#from rpython.jit.metainterp.resoperation import rop
from rpython.rlib.nonconst import NonConstant
from rpython.rlib import jit_hooks
from rpython.rlib.jit import Counters
from rpython.rlib.objectmodel import compute_unique_id
from pypy.module.pypyjit.interp_jit import pypyjitdriver

class Cache(object):
    in_recursion = False
    no = 0

    def __init__(self, space):
        self.w_compile_hook = space.w_None
        self.w_abort_hook = space.w_None

    def getno(self):
        self.no += 1
        return self.no - 1

def wrap_greenkey(space, jitdriver, greenkey, greenkey_repr):
    if greenkey is None:
        return space.w_None
    jitdriver_name = jitdriver.name
    if jitdriver_name == 'pypyjit':
        next_instr = greenkey[0].getint()
        is_being_profiled = greenkey[1].getint()
        ll_code = lltype.cast_opaque_ptr(lltype.Ptr(OBJECT),
                                         greenkey[2].getref_base())
        pycode = cast_base_ptr_to_instance(PyCode, ll_code)
        return space.newtuple([space.wrap(pycode), space.wrap(next_instr),
                               space.newbool(bool(is_being_profiled))])
    else:
        return space.wrap(greenkey_repr)

@unwrap_spec(operations=bool)
def set_compile_hook(space, w_hook, operations=True):
    """ set_compile_hook(hook, operations=True)

    Set a compiling hook that will be called each time a loop is compiled.

    The hook will be called with the pypyjit.JitLoopInfo object. Refer to it's
    docstring for details.

    Note that jit hook is not reentrant. It means that if the code
    inside the jit hook is itself jitted, it will get compiled, but the
    jit hook won't be called for that.
    """
    cache = space.fromcache(Cache)
    assert w_hook is not None
    cache.w_compile_hook = w_hook
    cache.compile_hook_with_ops = operations
    cache.in_recursion = NonConstant(False)

def set_abort_hook(space, w_hook):
    """ set_abort_hook(hook)

    Set a hook (callable) that will be called each time there is tracing
    aborted due to some reason.

    The hook will be called with the signature:

        hook(jitdriver_name, greenkey, reason, operations)

    Reason is a string, the meaning of other arguments is the same
    as attributes on JitLoopInfo object.
    """
    cache = space.fromcache(Cache)
    assert w_hook is not None
    cache.w_abort_hook = w_hook
    cache.in_recursion = NonConstant(False)

def wrap_oplist(space, logops, operations, ops_offset=None):
    # this function is called from the JIT
    from rpython.jit.metainterp.resoperation import rop
    
    l_w = []
    jitdrivers_sd = logops.metainterp_sd.jitdrivers_sd
    for op in operations:
        if ops_offset is None:
            ofs = -1
        else:
            ofs = ops_offset.get(op, 0)
        num = op.getopnum()
        name = op.getopname()
        if num == rop.DEBUG_MERGE_POINT:
            jd_sd = jitdrivers_sd[op.getarg(0).getint()]
            greenkey = op.getarglist()[3:]
            repr = jd_sd.warmstate.get_location_str(greenkey)
            w_greenkey = wrap_greenkey(space, jd_sd.jitdriver, greenkey, repr)
            l_w.append(DebugMergePoint(space, name,
                                       logops.repr_of_resop(op),
                                       jd_sd.jitdriver.name,
                                       op.getarg(1).getint(),
                                       op.getarg(2).getint(),
                                       w_greenkey))
        else:
            l_w.append(WrappedOp(name, ofs, logops.repr_of_resop(op)))
    return l_w

@unwrap_spec(offset=int, repr=str, name=str)
def descr_new_resop(space, w_tp, name, offset=-1, repr=''):
    return WrappedOp(name, offset, repr)

@unwrap_spec(repr=str, name=str, jd_name=str, call_depth=int, call_id=int)
def descr_new_dmp(space, w_tp, name, repr, jd_name, call_depth, call_id,
    w_greenkey):

    return DebugMergePoint(space, name,
                           repr, jd_name, call_depth, call_id, w_greenkey)


class WrappedOp(W_Root):
    """ A class representing a single ResOperation, wrapped nicely
    """
    def __init__(self, name, offset, repr_of_resop):
        self.offset = offset
        self.name = name
        self.repr_of_resop = repr_of_resop

    def descr_repr(self, space):
        return space.wrap(self.repr_of_resop)

    def descr_name(self, space):
        return space.wrap(self.name)

class DebugMergePoint(WrappedOp):
    """ A class representing Debug Merge Point - the entry point
    to a jitted loop.
    """

    def __init__(self, space, name, repr_of_resop, jd_name, call_depth,
                 call_id, w_greenkey):

        WrappedOp.__init__(self, name, -1, repr_of_resop)
        self.jd_name = jd_name
        self.call_depth = call_depth
        self.call_id = call_id
        self.w_greenkey = w_greenkey

    def get_pycode(self, space):
        if self.jd_name == pypyjitdriver.name:
            return space.getitem(self.w_greenkey, space.wrap(0))
        raise OperationError(space.w_AttributeError, space.wrap("This DebugMergePoint doesn't belong to the main Python JitDriver"))

    def get_bytecode_no(self, space):
        if self.jd_name == pypyjitdriver.name:
            return space.getitem(self.w_greenkey, space.wrap(1))
        raise OperationError(space.w_AttributeError, space.wrap("This DebugMergePoint doesn't belong to the main Python JitDriver"))

    def get_jitdriver_name(self, space):
        return space.wrap(self.jd_name)

WrappedOp.typedef = TypeDef(
    'ResOperation',
    __doc__ = WrappedOp.__doc__,
    __new__ = interp2app(descr_new_resop),
    __repr__ = interp2app(WrappedOp.descr_repr),
    name = GetSetProperty(WrappedOp.descr_name),
    offset = interp_attrproperty("offset", cls=WrappedOp),
)
WrappedOp.typedef.acceptable_as_base_class = False

DebugMergePoint.typedef = TypeDef(
    'DebugMergePoint', WrappedOp.typedef,
    __new__ = interp2app(descr_new_dmp),
    __doc__ = DebugMergePoint.__doc__,
    greenkey = interp_attrproperty_w("w_greenkey", cls=DebugMergePoint,
               doc="Representation of place where the loop was compiled. "
                    "In the case of the main interpreter loop, it's a triplet "
                    "(code, ofs, is_profiled)"),
    pycode = GetSetProperty(DebugMergePoint.get_pycode),
    bytecode_no = GetSetProperty(DebugMergePoint.get_bytecode_no,
                                 doc="offset in the bytecode"),
    call_depth = interp_attrproperty("call_depth", cls=DebugMergePoint,
                                     doc="Depth of calls within this loop"),
    call_id = interp_attrproperty("call_id", cls=DebugMergePoint,
                     doc="Number of applevel function traced in this loop"),
    jitdriver_name = GetSetProperty(DebugMergePoint.get_jitdriver_name,
                     doc="Name of the jitdriver 'pypyjit' in the case "
                                    "of the main interpreter loop"),
)
DebugMergePoint.typedef.acceptable_as_base_class = False


class W_JitLoopInfo(W_Root):
    """ Loop debug information
    """

    w_green_key = None
    bridge_no   = 0
    asmaddr     = 0
    asmlen      = 0

    def __init__(self, space, debug_info, is_bridge=False, wrap_ops=True):
        if wrap_ops:
            memo = {}
            logops = debug_info.logger._make_log_operations(memo)
            if debug_info.asminfo is not None:
                ofs = debug_info.asminfo.ops_offset
            else:
                ofs = {}
            ops = debug_info.operations
            self.w_ops = space.newlist(wrap_oplist(space, logops, ops, ofs))
        else:
            self.w_ops = space.w_None

        self.jd_name = debug_info.get_jitdriver().name
        self.type = debug_info.type
        if is_bridge:
            self.bridge_no = compute_unique_id(debug_info.fail_descr)
            #self.bridge_no = debug_info.fail_descr_no
            self.w_green_key = space.w_None
        else:
            self.w_green_key = wrap_greenkey(space,
                                             debug_info.get_jitdriver(),
                                             debug_info.greenkey,
                                             debug_info.get_greenkey_repr())
        self.loop_no = debug_info.looptoken.number
        asminfo = debug_info.asminfo
        if asminfo is not None:
            self.asmaddr = asminfo.asmaddr
            self.asmlen = asminfo.asmlen

    def descr_repr(self, space):
        lgt = space.int_w(space.len(self.w_ops))
        if self.type == "bridge":
            code_repr = 'bridge no %d' % self.bridge_no
        else:
            code_repr = space.str_w(space.repr(self.w_green_key))
        return space.wrap('<JitLoopInfo %s, %d operations, starting at <%s>>' %
                          (self.jd_name, lgt, code_repr))

    def descr_get_bridge_no(self, space):
        if space.is_none(self.w_green_key):
            return space.wrap(self.bridge_no)
        raise OperationError(space.w_TypeError, space.wrap("not a bridge"))


@unwrap_spec(loopno=int, asmaddr=int, asmlen=int, loop_no=int,
             type=str, jd_name=str, bridge_no=int)
def descr_new_jit_loop_info(space, w_subtype, w_greenkey, w_ops, loopno,
                            asmaddr, asmlen, loop_no, type, jd_name,
                            bridge_no=-1):
    w_info = space.allocate_instance(W_JitLoopInfo, w_subtype)
    w_info.w_green_key = w_greenkey
    w_info.w_ops = w_ops
    w_info.asmaddr = asmaddr
    w_info.asmlen = asmlen
    w_info.loop_no = loop_no
    w_info.type = type
    w_info.jd_name = jd_name
    w_info.bridge_no = bridge_no
    return w_info

W_JitLoopInfo.typedef = TypeDef(
    'JitLoopInfo',
    __doc__ = W_JitLoopInfo.__doc__,
    __new__ = interp2app(descr_new_jit_loop_info),
    jitdriver_name = interp_attrproperty('jd_name', cls=W_JitLoopInfo,
                       doc="Name of the JitDriver, pypyjit for the main one"),
    greenkey = interp_attrproperty_w('w_green_key', cls=W_JitLoopInfo,
               doc="Representation of place where the loop was compiled. "
                    "In the case of the main interpreter loop, it's a triplet "
                    "(code, ofs, is_profiled)"),
    operations = interp_attrproperty_w('w_ops', cls=W_JitLoopInfo, doc=
                                       "List of operations in this loop."),
    loop_no = interp_attrproperty('loop_no', cls=W_JitLoopInfo, doc=
                                  "Loop cardinal number"),
    bridge_no = GetSetProperty(W_JitLoopInfo.descr_get_bridge_no,
                               doc="bridge number (if a bridge)"),
    type = interp_attrproperty('type', cls=W_JitLoopInfo,
                               doc="Loop type"),
    asmaddr = interp_attrproperty('asmaddr', cls=W_JitLoopInfo,
                                  doc="Address of machine code"),
    asmlen = interp_attrproperty('asmlen', cls=W_JitLoopInfo,
                                  doc="Length of machine code"),
    __repr__ = interp2app(W_JitLoopInfo.descr_repr),
)
W_JitLoopInfo.typedef.acceptable_as_base_class = False


class W_JitInfoSnapshot(W_Root):
    def __init__(self, space, w_times, w_counters, w_counter_times):
        self.w_loop_run_times = w_times
        self.w_counters = w_counters
        self.w_counter_times = w_counter_times

W_JitInfoSnapshot.typedef = TypeDef(
    "JitInfoSnapshot",
    loop_run_times = interp_attrproperty_w("w_loop_run_times",
                                             cls=W_JitInfoSnapshot),
    counters = interp_attrproperty_w("w_counters",
                                       cls=W_JitInfoSnapshot,
                                       doc="various JIT counters"),
    counter_times = interp_attrproperty_w("w_counter_times",
                                            cls=W_JitInfoSnapshot,
                                            doc="various JIT timers")
)
W_JitInfoSnapshot.typedef.acceptable_as_base_class = False

def get_stats_snapshot(space):
    """ Get the jit status in the specific moment in time. Note that this
    is eager - the attribute access is not lazy, if you need new stats
    you need to call this function again.
    """
    ll_times = jit_hooks.stats_get_loop_run_times(None)
    w_times = space.newdict()
    for i in range(len(ll_times)):
        w_key = space.newtuple([space.wrap(ll_times[i].type),
                                space.wrap(ll_times[i].number)])
        space.setitem(w_times, w_key,
                      space.wrap(ll_times[i].counter))
    w_counters = space.newdict()
    for i, counter_name in enumerate(Counters.counter_names):
        v = jit_hooks.stats_get_counter_value(None, i)
        space.setitem_str(w_counters, counter_name, space.wrap(v))
    w_counter_times = space.newdict()
    tr_time = jit_hooks.stats_get_times_value(None, Counters.TRACING)
    space.setitem_str(w_counter_times, 'TRACING', space.wrap(tr_time))
    b_time = jit_hooks.stats_get_times_value(None, Counters.BACKEND)
    space.setitem_str(w_counter_times, 'BACKEND', space.wrap(b_time))
    return space.wrap(W_JitInfoSnapshot(space, w_times, w_counters,
                                        w_counter_times))

def enable_debug(space):
    """ Set the jit debugging - completely necessary for some stats to work,
    most notably assembler counters.
    """
    jit_hooks.stats_set_debug(None, True)

def disable_debug(space):
    """ Disable the jit debugging. This means some very small loops will be
    marginally faster and the counters will stop working.
    """
    jit_hooks.stats_set_debug(None, False)

from rpython.jit.metainterp import jitprof, resume, compile
from rpython.jit.metainterp.executor import execute_nonspec_const
from rpython.jit.metainterp.logger import LogOperations
from rpython.jit.metainterp.history import Const, ConstInt, REF, ConstPtr
from rpython.jit.metainterp.optimizeopt.intutils import IntBound,\
     ConstIntBound, MININT, MAXINT, IntUnbounded
from rpython.jit.metainterp.optimizeopt.util import make_dispatcher_method
from rpython.jit.metainterp.resoperation import rop, AbstractResOp, GuardResOp,\
     OpHelpers, ResOperation
from rpython.jit.metainterp.optimizeopt import info
from rpython.jit.metainterp.typesystem import llhelper
from rpython.rlib.objectmodel import specialize, we_are_translated




CONST_0      = ConstInt(0)
CONST_1      = ConstInt(1)
CONST_ZERO_FLOAT = Const._new(0.0)
llhelper.CONST_NULLREF = llhelper.CONST_NULL
REMOVED = AbstractResOp()

class LoopInfo(object):
    pass

class BasicLoopInfo(LoopInfo):
    def __init__(self, inputargs, quasi_immutable_deps):
        self.inputargs = inputargs
        self.label_op = ResOperation(rop.LABEL, inputargs)
        self.quasi_immutable_deps = quasi_immutable_deps
        self.extra_same_as = []

    def final(self):
        return True


class Optimization(object):
    next_optimization = None
    potential_extra_ops = None

    def __init__(self):
        pass # make rpython happy

    def send_extra_operation(self, op):
        self.optimizer.send_extra_operation(op)

    def propagate_forward(self, op):
        raise NotImplementedError

    def emit_operation(self, op):
        self.last_emitted_operation = op
        self.next_optimization.propagate_forward(op)

    def getintbound(self, op):
        assert op.type == 'i'
        op = self.get_box_replacement(op)
        if isinstance(op, ConstInt):
            return ConstIntBound(op.getint())
        fw = op.get_forwarded()
        if fw is not None:
            if isinstance(fw, IntBound):
                return fw
            # rare case: fw might be a RawBufferPtrInfo
            return IntUnbounded()
        assert op.type == 'i'
        intbound = IntBound(MININT, MAXINT)
        op.set_forwarded(intbound)
        return intbound

    def setintbound(self, op, bound):
        assert op.type == 'i'
        op = self.get_box_replacement(op)
        if op.is_constant():
            return
        cur = op.get_forwarded()
        if cur is not None:
            if isinstance(cur, IntBound):
                cur.intersect(bound)
        else:
            op.set_forwarded(bound)

    def getnullness(self, op):
        if op.type == 'r' or self.is_raw_ptr(op):
            ptrinfo = self.getptrinfo(op)
            if ptrinfo is None:
                return info.INFO_UNKNOWN
            return ptrinfo.getnullness()
        elif op.type == 'i':
            return self.getintbound(op).getnullness()
        assert False

    def make_constant_class(self, op, class_const, update_last_guard=True):
        op = self.get_box_replacement(op)
        opinfo = op.get_forwarded()
        if isinstance(opinfo, info.InstancePtrInfo):
            opinfo._known_class = class_const
        else:
            if opinfo is not None:
                last_guard_pos = opinfo.get_last_guard_pos()
            else:
                last_guard_pos = -1
            opinfo = info.InstancePtrInfo(None, class_const)
            opinfo.last_guard_pos = last_guard_pos
            op.set_forwarded(opinfo)
        if update_last_guard:
            opinfo.mark_last_guard(self.optimizer)
        return opinfo

    def getptrinfo(self, op, is_object=False):
        if op.type == 'i':
            return self.getrawptrinfo(op)
        elif op.type == 'f':
            return None
        assert op.type == 'r'
        op = self.get_box_replacement(op)
        assert op.type == 'r'
        if isinstance(op, ConstPtr):
            return info.ConstPtrInfo(op)
        fw = op.get_forwarded()
        if fw is not None:
            assert isinstance(fw, info.PtrInfo)
            return fw
        return None

    def is_raw_ptr(self, op):
        fw = self.get_box_replacement(op).get_forwarded()
        if isinstance(fw, info.AbstractRawPtrInfo):
            return True
        return False
    
    def getrawptrinfo(self, op, create=False, is_object=False):
        assert op.type == 'i'
        op = self.get_box_replacement(op)
        assert op.type == 'i'
        if isinstance(op, ConstInt):
            return info.ConstPtrInfo(op)
        fw = op.get_forwarded()
        if isinstance(fw, IntBound) and not create:
            return None
        if fw is not None:
            if isinstance(fw, info.AbstractRawPtrInfo):
                return fw
            fw = info.RawStructPtrInfo()
            op.set_forwarded(fw)
            assert isinstance(fw, info.AbstractRawPtrInfo)
            return fw
        return None

    def get_box_replacement(self, op, not_const=False):
        return self.optimizer.get_box_replacement(op, not_const=not_const)

    def getlastop(self):
        return self.optimizer.getlastop()

    def force_box(self, op, optforce=None):
        return self.optimizer.force_box(op, optforce)

    def replace_op_with(self, op, newopnum, args=None, descr=None):
        return self.optimizer.replace_op_with(op, newopnum, args, descr)

    def ensure_ptr_info_arg0(self, op):
        return self.optimizer.ensure_ptr_info_arg0(op)

    def make_constant(self, box, constbox):
        return self.optimizer.make_constant(box, constbox)

    def make_constant_int(self, box, intconst):
        return self.optimizer.make_constant_int(box, intconst)

    def make_equal_to(self, box, value):
        return self.optimizer.make_equal_to(box, value)

    def make_nonnull(self, op):
        return self.optimizer.make_nonnull(op)

    def make_nonnull_str(self, op, mode):
        return self.optimizer.make_nonnull_str(op, mode)

    def get_constant_box(self, box):
        return self.optimizer.get_constant_box(box)

    def new_box(self, fieldofs):
        return self.optimizer.new_box(fieldofs)

    def new_const(self, fieldofs):
        return self.optimizer.new_const(fieldofs)

    def new_box_item(self, arraydescr):
        return self.optimizer.new_box_item(arraydescr)

    def new_const_item(self, arraydescr):
        return self.optimizer.new_const_item(arraydescr)

    def pure(self, opnum, result):
        if self.optimizer.optpure:
            self.optimizer.optpure.pure(opnum, result)

    def pure_from_args(self, opnum, args, op, descr=None):
        if self.optimizer.optpure:
            self.optimizer.optpure.pure_from_args(opnum, args, op, descr)

    def has_pure_result(self, opnum, args, descr):
        if self.optimizer.optpure:
            return self.optimizer.optpure.has_pure_result(opnum, args, descr)
        return False

    def get_pure_result(self, key):
        if self.optimizer.optpure:
            return self.optimizer.optpure.get_pure_result(key)
        return None

    def setup(self):
        pass

    # Called after last operation has been propagated to flush out any posponed ops
    def flush(self):
        pass

    def produce_potential_short_preamble_ops(self, potential_ops):
        pass

    def forget_numberings(self):
        self.optimizer.forget_numberings()

    def _can_optimize_call_pure(self, op):
        arg_consts = []
        for i in range(op.numargs()):
            arg = op.getarg(i)
            const = self.optimizer.get_constant_box(arg)
            if const is None:
                return None
            arg_consts.append(const)
        else:
            # all constant arguments: check if we already know the result
            try:
                return self.optimizer.call_pure_results[arg_consts]
            except KeyError:
                return None


class Optimizer(Optimization):

    def __init__(self, metainterp_sd, jitdriver_sd, optimizations=None):
        self.metainterp_sd = metainterp_sd
        self.jitdriver_sd = jitdriver_sd
        self.cpu = metainterp_sd.cpu
        self.interned_refs = self.cpu.ts.new_ref_dict()
        self.interned_ints = {}
        self.resumedata_memo = resume.ResumeDataLoopMemo(metainterp_sd)
        self.pendingfields = None # set temporarily to a list, normally by
                                  # heap.py, as we're about to generate a guard
        self.quasi_immutable_deps = None
        self.opaque_pointers = {}
        self.replaces_guard = {}
        self._newoperations = []
        self.optimizer = self
        self.optpure = None
        self.optheap = None
        self.optrewrite = None
        self.optearlyforce = None
        self.optunroll = None

        self.set_optimizations(optimizations)
        self.setup()

    def init_inparg_dict_from(self, lst):
        self.inparg_dict = {}
        for box in lst:
            self.inparg_dict[box] = None

    def set_optimizations(self, optimizations):
        if optimizations:
            self.first_optimization = optimizations[0]
            for i in range(1, len(optimizations)):
                optimizations[i - 1].next_optimization = optimizations[i]
            optimizations[-1].next_optimization = self
            for o in optimizations:
                o.optimizer = self
                o.last_emitted_operation = None
                o.setup()
        else:
            optimizations = []
            self.first_optimization = self

        self.optimizations  = optimizations

    def force_op_from_preamble(self, op):
        return op

    def notice_guard_future_condition(self, op):
        self.patchguardop = op

    def replace_guard(self, op, value):
        assert isinstance(value, info.NonNullPtrInfo)
        if value.last_guard_pos == -1:
            return
        self.replaces_guard[op] = value.last_guard_pos

    def force_box_for_end_of_preamble(self, box):
        if box.type == 'r':
            info = self.getptrinfo(box)
            if info is not None and info.is_virtual():
                rec = {}
                return info.force_at_the_end_of_preamble(box,
                                                self.optearlyforce, rec)
            return box
        if box.type == 'i':
            info = self.getrawptrinfo(box)
            if info is not None:
                return info.force_at_the_end_of_preamble(box,
                                            self.optearlyforce, None)
        return box

    def flush(self):
        for o in self.optimizations:
            o.flush()

    def produce_potential_short_preamble_ops(self, sb):
        for opt in self.optimizations:
            opt.produce_potential_short_preamble_ops(sb)

    def forget_numberings(self):
        self.metainterp_sd.profiler.count(jitprof.Counters.OPT_FORCINGS)
        self.resumedata_memo.forget_numberings()

    def getinfo(self, op):
        if op.type == 'r':
            return self.getptrinfo(op)
        elif op.type == 'i':
            if self.is_raw_ptr(op):
                return self.getptrinfo(op)
            return self.getintbound(op)
        elif op.type == 'f':
            if self.get_box_replacement(op).is_constant():
                return info.FloatConstInfo(self.get_box_replacement(op))

    def get_box_replacement(self, op, not_const=False):
        if op is None:
            return op
        return op.get_box_replacement(not_const)

    def force_box(self, op, optforce=None):
        op = self.get_box_replacement(op)
        if optforce is None:
            optforce = self
        info = op.get_forwarded()
        if self.optunroll and self.optunroll.potential_extra_ops:
            # XXX hack
            try:
                preamble_op = self.optunroll.potential_extra_ops.pop(op)
            except KeyError:
                pass
            else:
                sb = self.optunroll.short_preamble_producer
                sb.add_preamble_op(preamble_op)
        if info is not None:
            if op.type == 'i' and info.is_constant():
                return ConstInt(info.getint())
            return info.force_box(op, optforce)
        return op

    def is_inputarg(self, op):
        return True
        return op in self.inparg_dict

    def get_constant_box(self, box):
        box = self.get_box_replacement(box)
        if isinstance(box, Const):
            return box
        if (box.type == 'i' and box.get_forwarded() and
            box.get_forwarded().is_constant()):
            return ConstInt(box.get_forwarded().getint())
        #self.ensure_imported(value)

    def get_newoperations(self):
        self.flush()
        return self._newoperations

    def clear_newoperations(self):
        self._newoperations = []

    def make_equal_to(self, op, newop):
        op = self.get_box_replacement(op)
        if op is newop:
            return
        opinfo = op.get_forwarded()
        if opinfo is not None:
            assert isinstance(opinfo, info.AbstractInfo)
            op.set_forwarded(newop)
            if not isinstance(newop, Const):
                newop.set_forwarded(opinfo)
        else:
            op.set_forwarded(newop)

    def replace_op_with(self, op, newopnum, args=None, descr=None):
        newop = op.copy_and_change(newopnum, args, descr)
        if newop.type != 'v':
            op = self.get_box_replacement(op)
            opinfo = op.get_forwarded()
            if opinfo is not None:
                newop.set_forwarded(opinfo)
            op.set_forwarded(newop)
        return newop

    def make_constant(self, box, constbox):
        assert isinstance(constbox, Const)
        box = self.get_box_replacement(box)
        if not we_are_translated():    # safety-check
            if (box.get_forwarded() is not None and
                isinstance(constbox, ConstInt) and
                not isinstance(box.get_forwarded(), info.AbstractRawPtrInfo)):
                assert box.get_forwarded().contains(constbox.getint())
        if box.is_constant():
            return
        if box.type == 'r' and box.get_forwarded() is not None:
            opinfo = box.get_forwarded()
            opinfo.copy_fields_to_const(self.getptrinfo(constbox), self.optheap)
        box.set_forwarded(constbox)

    def make_constant_int(self, box, intvalue):
        self.make_constant(box, ConstInt(intvalue))

    def make_nonnull(self, op):
        op = self.get_box_replacement(op)
        if op.is_constant():
            return
        if op.type == 'i':
            # raw pointers
            return
        opinfo = op.get_forwarded()
        if opinfo is not None:
            assert opinfo.is_nonnull()
            return
        op.set_forwarded(info.NonNullPtrInfo())

    def make_nonnull_str(self, op, mode):
        from rpython.jit.metainterp.optimizeopt import vstring
        
        op = self.get_box_replacement(op)
        if op.is_constant():
            return
        opinfo = op.get_forwarded()
        if isinstance(opinfo, vstring.StrPtrInfo):
            return
        op.set_forwarded(vstring.StrPtrInfo(mode))

    def ensure_ptr_info_arg0(self, op):
        from rpython.jit.metainterp.optimizeopt import vstring
        
        arg0 = self.get_box_replacement(op.getarg(0))
        if arg0.is_constant():
            return info.ConstPtrInfo(arg0)
        opinfo = arg0.get_forwarded()
        if isinstance(opinfo, info.AbstractVirtualPtrInfo):
            return opinfo
        elif opinfo is not None:
            last_guard_pos = opinfo.get_last_guard_pos()
        else:
            last_guard_pos = -1
        assert opinfo is None or opinfo.__class__ is info.NonNullPtrInfo
        if (op.is_getfield() or op.getopnum() == rop.SETFIELD_GC or
            op.getopnum() == rop.QUASIIMMUT_FIELD):
            descr = op.getdescr()
            parent_descr = descr.get_parent_descr()
            if parent_descr.is_object():
                opinfo = info.InstancePtrInfo(parent_descr)
            else:
                opinfo = info.StructPtrInfo(parent_descr)
            opinfo.init_fields(parent_descr, descr.get_index())
        elif (op.is_getarrayitem() or op.getopnum() == rop.SETARRAYITEM_GC or
              op.getopnum() == rop.ARRAYLEN_GC):
            opinfo = info.ArrayPtrInfo(op.getdescr())
        elif op.getopnum() in (rop.GUARD_CLASS, rop.GUARD_NONNULL_CLASS):
            opinfo = info.InstancePtrInfo()
        elif op.getopnum() in (rop.STRLEN,):
            opinfo = vstring.StrPtrInfo(vstring.mode_string)            
        elif op.getopnum() in (rop.UNICODELEN,):
            opinfo = vstring.StrPtrInfo(vstring.mode_unicode)
        else:
            assert False, "operations %s unsupported" % op
        assert isinstance(opinfo, info.NonNullPtrInfo)
        opinfo.last_guard_pos = last_guard_pos
        arg0.set_forwarded(opinfo)
        return opinfo

    def new_const(self, fieldofs):
        if fieldofs.is_pointer_field():
            return self.cpu.ts.CONST_NULL
        elif fieldofs.is_float_field():
            return CONST_ZERO_FLOAT
        else:
            return CONST_0

    def new_const_item(self, arraydescr):
        if arraydescr.is_array_of_pointers():
            return self.cpu.ts.CONST_NULL
        elif arraydescr.is_array_of_floats():
            return CONST_ZERO_FLOAT
        else:
            return CONST_0

    def propagate_all_forward(self, inputargs, ops, call_pure_results=None,
                              rename_inputargs=True, flush=True):
        if rename_inputargs:
            newargs = []
            for inparg in inputargs:
                new_arg = OpHelpers.inputarg_from_tp(inparg.type)
                inparg.set_forwarded(new_arg)
                newargs.append(new_arg)
            self.init_inparg_dict_from(newargs)
        else:
            newargs = inputargs
        self.call_pure_results = call_pure_results
        if ops[-1].getopnum() in (rop.FINISH, rop.JUMP):
            last = len(ops) - 1
            extra_jump = True
        else:
            extra_jump = False
            last = len(ops)
        for i in range(last):
            self._really_emitted_operation = None
            self.first_optimization.propagate_forward(ops[i])
        # accumulate counters
        if flush:
            self.flush()
        if extra_jump:
            self.first_optimization.propagate_forward(ops[-1])
        self.resumedata_memo.update_counters(self.metainterp_sd.profiler)
        return (BasicLoopInfo(newargs, self.quasi_immutable_deps),
                self._newoperations)

    def _clean_optimization_info(self, lst):
        for op in lst:
            if op.get_forwarded() is not None:
                op.set_forwarded(None)

    def send_extra_operation(self, op):
        self.first_optimization.propagate_forward(op)

    def propagate_forward(self, op):
        dispatch_opt(self, op)

    def emit_operation(self, op):
        if op.returns_bool_result():
            self.getintbound(op).make_bool()
        self._emit_operation(op)
        op = self.get_box_replacement(op)
        if op.type == 'i':
            opinfo = op.get_forwarded()
            if opinfo is not None:
                assert isinstance(opinfo, IntBound)
                if opinfo.is_constant():
                    op.set_forwarded(ConstInt(opinfo.getint()))

    @specialize.argtype(0)
    def _emit_operation(self, op):
        assert not op.is_call_pure()
        orig_op = op
        op = self.get_box_replacement(op)
        if op.is_constant():
            return # can happen e.g. if we postpone the operation that becomes
            # constant
        op = self.replace_op_with(op, op.getopnum())
        for i in range(op.numargs()):
            arg = self.force_box(op.getarg(i))
            op.setarg(i, arg)
        self.metainterp_sd.profiler.count(jitprof.Counters.OPT_OPS)
        if op.is_guard():
            self.metainterp_sd.profiler.count(jitprof.Counters.OPT_GUARDS)
            pendingfields = self.pendingfields
            self.pendingfields = None
            if self.replaces_guard and orig_op in self.replaces_guard:
                self.replace_guard_op(self.replaces_guard[orig_op], op)
                del self.replaces_guard[orig_op]
                return
            else:
                guard_op = self.replace_op_with(op, op.getopnum())
                op = self.store_final_boxes_in_guard(guard_op, pendingfields)
                # for unrolling
                for farg in op.getfailargs():
                    if farg:
                        self.force_box(farg)
        elif op.can_raise():
            self.exception_might_have_happened = True
        self._really_emitted_operation = op
        self._newoperations.append(op)

    def getlastop(self):
        return self._really_emitted_operation

    def replace_guard_op(self, old_op_pos, new_op):
        old_op = self._newoperations[old_op_pos]
        assert old_op.is_guard()
        old_descr = old_op.getdescr()
        new_descr = new_op.getdescr()
        new_descr.copy_all_attributes_from(old_descr)
        self._newoperations[old_op_pos] = new_op

    def store_final_boxes_in_guard(self, op, pendingfields):
        assert pendingfields is not None
        if op.getdescr() is not None:
            descr = op.getdescr()
            assert isinstance(descr, compile.ResumeAtPositionDescr)
        else:
            descr = compile.invent_fail_descr_for_op(op.getopnum(), self)
            op.setdescr(descr)
        assert isinstance(descr, compile.ResumeGuardDescr)
        assert isinstance(op, GuardResOp)
        modifier = resume.ResumeDataVirtualAdder(self, descr, op,
                                                 self.resumedata_memo)
        try:
            newboxes = modifier.finish(self, pendingfields)
            if (newboxes is not None and
                len(newboxes) > self.metainterp_sd.options.failargs_limit):
                raise resume.TagOverflow
        except resume.TagOverflow:
            raise compile.giveup()
        # check no duplicates
        #if not we_are_translated():
        seen = {}
        for box in newboxes:
            if box is not None:
                assert box not in seen
                seen[box] = None
        descr.store_final_boxes(op, newboxes, self.metainterp_sd)
        #
        if op.getopnum() == rop.GUARD_VALUE:
            if op.getarg(0).type == 'i':
                b = self.getintbound(op.getarg(0))
                if b.is_bool():
                    # Hack: turn guard_value(bool) into guard_true/guard_false.
                    # This is done after the operation is emitted to let
                    # store_final_boxes_in_guard set the guard_opnum field of
                    # the descr to the original rop.GUARD_VALUE.
                    constvalue = op.getarg(1).getint()
                    if constvalue == 0:
                        opnum = rop.GUARD_FALSE
                    elif constvalue == 1:
                        opnum = rop.GUARD_TRUE
                    else:
                        raise AssertionError("uh?")
                    newop = self.replace_op_with(op, opnum, [op.getarg(0)], descr)
                    return newop
            # a real GUARD_VALUE.  Make it use one counter per value.
            descr.make_a_counter_per_value(op)
        return op

    def optimize_default(self, op):
        self.emit_operation(op)

    def constant_fold(self, op):
        argboxes = [self.get_constant_box(op.getarg(i))
                    for i in range(op.numargs())]
        return execute_nonspec_const(self.cpu, None,
                                       op.getopnum(), argboxes,
                                       op.getdescr(), op.type)

    def is_virtual(self, op):
        if op.type == 'r':
            opinfo = self.getptrinfo(op)
            return opinfo is not None and opinfo.is_virtual()
        if op.type == 'i':
            opinfo = self.getrawptrinfo(op)
            return opinfo is not None and opinfo.is_virtual()
        return False

    def pure_reverse(self, op):
        import sys
        if self.optpure is None:
            return
        optpure = self.optpure
        if op.getopnum() == rop.INT_ADD:
            arg0 = op.getarg(0)
            arg1 = op.getarg(1)
            optpure.pure_from_args(rop.INT_ADD, [arg1, arg0], op)
            # Synthesize the reverse op for optimize_default to reuse
            optpure.pure_from_args(rop.INT_SUB, [op, arg1], arg0)
            optpure.pure_from_args(rop.INT_SUB, [op, arg0], arg1)
            if isinstance(arg0, ConstInt):
                # invert the constant
                i0 = arg0.getint()
                if i0 == -sys.maxint - 1:
                    return
                inv_arg0 = ConstInt(-i0)
            elif isinstance(arg1, ConstInt):
                # commutative
                i0 = arg1.getint()
                if i0 == -sys.maxint - 1:
                    return
                inv_arg0 = ConstInt(-i0)
                arg1 = arg0
            else:
                return
            optpure.pure_from_args(rop.INT_SUB, [arg1, inv_arg0], op)
            optpure.pure_from_args(rop.INT_SUB, [arg1, op], inv_arg0)
            optpure.pure_from_args(rop.INT_ADD, [op, inv_arg0], arg1)
            optpure.pure_from_args(rop.INT_ADD, [inv_arg0, op], arg1)

        elif op.getopnum() == rop.INT_SUB:
            arg0 = op.getarg(0)
            arg1 = op.getarg(1)
            optpure.pure_from_args(rop.INT_ADD, [op, arg1], arg0)
            optpure.pure_from_args(rop.INT_SUB, [arg0, op], arg1)
            if isinstance(arg1, ConstInt):
                # invert the constant
                i1 = arg1.getint()
                if i1 == -sys.maxint - 1:
                    return
                inv_arg1 = ConstInt(-i1)
                optpure.pure_from_args(rop.INT_ADD, [arg0, inv_arg1], op)
                optpure.pure_from_args(rop.INT_ADD, [inv_arg1, arg0], op)
                optpure.pure_from_args(rop.INT_SUB, [op, inv_arg1], arg0)
                optpure.pure_from_args(rop.INT_SUB, [op, arg0], inv_arg1)
        elif op.getopnum() == rop.FLOAT_MUL:
            optpure.pure_from_args(rop.FLOAT_MUL,
                                   [op.getarg(1), op.getarg(0)], op)
        elif op.getopnum() == rop.FLOAT_NEG:
            optpure.pure_from_args(rop.FLOAT_NEG, [op], op.getarg(0))
        elif op.getopnum() == rop.CAST_INT_TO_PTR:
            optpure.pure_from_args(rop.CAST_PTR_TO_INT, [op], op.getarg(0))
        elif op.getopnum() == rop.CAST_PTR_TO_INT:
            optpure.pure_from_args(rop.CAST_INT_TO_PTR, [op], op.getarg(0))

    #def optimize_GUARD_NO_OVERFLOW(self, op):
    #    # otherwise the default optimizer will clear fields, which is unwanted
    #    # in this case
    #    self.emit_operation(op)
    # FIXME: Is this still needed?

    def optimize_DEBUG_MERGE_POINT(self, op):
        self.emit_operation(op)

    def optimize_JIT_DEBUG(self, op):
        self.emit_operation(op)

    def optimize_STRGETITEM(self, op):
        indexb = self.getintbound(op.getarg(1))
        if indexb.is_constant():
            pass
            #raise Exception("implement me")
            #arrayvalue = self.getvalue(op.getarg(0))
            #arrayvalue.make_len_gt(MODE_STR, op.getdescr(), indexvalue.box.getint())
        self.optimize_default(op)

    def optimize_UNICODEGETITEM(self, op):
        indexb = self.getintbound(op.getarg(1))
        if indexb.is_constant():
            #arrayvalue = self.getvalue(op.getarg(0))
            #arrayvalue.make_len_gt(MODE_UNICODE, op.getdescr(), indexvalue.box.getint())
            pass
        self.optimize_default(op)

    # These are typically removed already by OptRewrite, but it can be
    # dissabled and unrolling emits some SAME_AS ops to setup the
    # optimizier state. These needs to always be optimized out.
    def optimize_SAME_AS_I(self, op):
        self.make_equal_to(op, op.getarg(0))
    optimize_SAME_AS_R = optimize_SAME_AS_I
    optimize_SAME_AS_F = optimize_SAME_AS_I

dispatch_opt = make_dispatcher_method(Optimizer, 'optimize_',
        default=Optimizer.optimize_default)

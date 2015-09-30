from pypy.interpreter.error import OperationError, oefmt
from pypy.interpreter.gateway import unwrap_spec, WrappedDefault
from pypy.module._cffi_backend import ctypeobj, cdataobj, allocator


# ____________________________________________________________

@unwrap_spec(w_ctype=ctypeobj.W_CType, w_init=WrappedDefault(None))
def newp(space, w_ctype, w_init):
    return w_ctype.newp(w_init, allocator.default_allocator)

# ____________________________________________________________

@unwrap_spec(w_ctype=ctypeobj.W_CType)
def cast(space, w_ctype, w_ob):
    return w_ctype.cast(w_ob)

# ____________________________________________________________

@unwrap_spec(w_ctype=ctypeobj.W_CType)
def callback(space, w_ctype, w_callable, w_error=None, w_onerror=None):
    from pypy.module._cffi_backend.ccallback import W_CDataCallback
    return W_CDataCallback(space, w_ctype, w_callable, w_error, w_onerror)

# ____________________________________________________________

@unwrap_spec(w_cdata=cdataobj.W_CData)
def typeof(space, w_cdata):
    return w_cdata.ctype

# ____________________________________________________________

def sizeof(space, w_obj):
    if isinstance(w_obj, cdataobj.W_CData):
        size = w_obj._sizeof()
    elif isinstance(w_obj, ctypeobj.W_CType):
        size = w_obj.size
        if size < 0:
            raise oefmt(space.w_ValueError,
                        "ctype '%s' is of unknown size", w_obj.name)
    else:
        raise OperationError(space.w_TypeError,
                            space.wrap("expected a 'cdata' or 'ctype' object"))
    return space.wrap(size)

@unwrap_spec(w_ctype=ctypeobj.W_CType)
def alignof(space, w_ctype):
    align = w_ctype.alignof()
    return space.wrap(align)

@unwrap_spec(w_ctype=ctypeobj.W_CType, following=int)
def typeoffsetof(space, w_ctype, w_field_or_index, following=0):
    ctype, offset = w_ctype.direct_typeoffsetof(w_field_or_index, following)
    return space.newtuple([space.wrap(ctype), space.wrap(offset)])

@unwrap_spec(w_ctype=ctypeobj.W_CType, w_cdata=cdataobj.W_CData, offset=int)
def rawaddressof(space, w_ctype, w_cdata, offset):
    return w_ctype.rawaddressof(w_cdata, offset)

# ____________________________________________________________

@unwrap_spec(w_ctype=ctypeobj.W_CType, replace_with=str)
def getcname(space, w_ctype, replace_with):
    p = w_ctype.name_position
    s = '%s%s%s' % (w_ctype.name[:p], replace_with, w_ctype.name[p:])
    return space.wrap(s)

# ____________________________________________________________

@unwrap_spec(w_cdata=cdataobj.W_CData, maxlen=int)
def string(space, w_cdata, maxlen=-1):
    return w_cdata.ctype.string(w_cdata, maxlen)

# ____________________________________________________________

def _get_types(space):
    return space.newtuple([space.gettypefor(cdataobj.W_CData),
                           space.gettypefor(ctypeobj.W_CType)])

# ____________________________________________________________

@unwrap_spec(w_ctype=ctypeobj.W_CType)
def from_buffer(space, w_ctype, w_x):
    from pypy.module._cffi_backend import ctypearray, ctypeprim
    #
    if (not isinstance(w_ctype, ctypearray.W_CTypeArray) or
        not isinstance(w_ctype.ctptr.ctitem, ctypeprim.W_CTypePrimitiveChar)):
        raise oefmt(space.w_TypeError,
                    "needs 'char[]', got '%s'", w_ctype.name)
    #
    # xxx do we really need to implement the same mess as in CPython 2.7
    # w.r.t. buffers and memoryviews??
    try:
        buf = space.readbuf_w(w_x)
    except OperationError, e:
        if not e.match(space, space.w_TypeError):
            raise
        buf = space.buffer_w(w_x, space.BUF_SIMPLE)
    try:
        _cdata = buf.get_raw_address()
    except ValueError:
        raise oefmt(space.w_TypeError,
                    "from_buffer() got a '%T' object, which supports the "
                    "buffer interface but cannot be rendered as a plain "
                    "raw address on PyPy", w_x)
    #
    return cdataobj.W_CDataFromBuffer(space, _cdata, w_ctype, buf, w_x)

# ____________________________________________________________

@unwrap_spec(w_cdata=cdataobj.W_CData)
def gcp(space, w_cdata, w_destructor):
    return w_cdata.with_gc(w_destructor)

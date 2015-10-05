:- use_module(library(clpfd)).
 
layout(Vars) :-
    Vars = [Gap,Pw,Lw,Rw],
    Pw #= 40000,
    Gap * 20000 #= Pw,
    Lw + Gap + Rw #= Pw,
    Lw #>= 0,
    Rw #>= 0,
    Gap #= 2,
    Lw #= 0.

bench(Count) :-
    T1 is cputime * 1000,
    dobench(Count),
    T2 is cputime * 1000,
    report(Count, T1, T2).

dobench(Count) :-
    nrepeat(Count),
    Vars = [Gap,Pw,Lw,Rw],
    layout(Vars),
    label(Vars),
    write(Vars),
    nl,
    fail.
dobench(_).

nrepeat(_).
nrepeat(N) :-
   N>1,
   N1 is N-1,
   nrepeat(N1).

report(Count, T1, T2) :-
    Time is T2-T1,
    nl,
    write('THIS IS THE TIME: '),
    write(Time),
    nl.

%% Vars=[S,E,N,D,M,O,R,Y], sendmoremoney(Vars), label(Vars).
%% bench(10).
%% exit().

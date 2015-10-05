:- use_module(library(clpfd)).
 
animals(Vars) :-
    Animals is 100,
    Cents is 10000,
    Dogc is 1500,
    Catc is 100,
    Micec is 25,
    Vars = [Dog,Cat,Mouse],
    Vars ins 1..Animals,
    Dogc*Dog + Catc*Cat + Micec*Mouse #= Cents,
    Dog + Cat + Mouse #= Animals.

bench(Count) :-
    T1 is cputime,
    dobench(Count),
    T2 is cputime,
    report(Count, T1, T2).

dobench(Count) :-
    nrepeat(Count),
    Vars = [Dog,Cat,Mouse],
    animals(Vars),
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

%% bench(50).
% exit().

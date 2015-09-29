:- use_module(library(clpfd)).
 
sendmoremoney(Vars) :-
    Vars = [S,E,N,D,M,O,R,Y],
    Vars ins 0..9,
    S #\= 0,
    M #\= 0,
    all_different(Vars),
                 1000*S + 100*E + 10*N + D
    +            1000*M + 100*O + 10*R + E
    #= 10000*M + 1000*O + 100*N + 10*E + Y.

bench(Count) :-
    T1 is cputime,
    dobench(Count),
    T2 is cputime,
    report(Count, T1, T2).

dobench(Count) :-
    nrepeat(Count),
    Vars = [S,E,N,D,M,O,R,Y],
    sendmoremoney(Vars),
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
    write(Time),
    nl.

%% Vars=[S,E,N,D,M,O,R,Y], sendmoremoney(Vars), label(Vars).

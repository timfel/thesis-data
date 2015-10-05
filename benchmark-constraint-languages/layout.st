'From Squeak4.5 of 19 February 2014 [latest update: #13680] on 30 September 2015 at 11:09:18 am'!
Object subclass: #ConstraintMockObject
        instanceVariableNames: 'gap pw lw rw'
        classVariableNames: ''
        poolDictionaries: ''
        category: 'Constraints-Benchmarks'!

!ConstraintMockObject methodsFor: 'initialize-release' stamp: 'tfel 9/23/2015 15:38'!
initialize

        gap := 0.
        pw := 0.
        lw := 0.
        rw := 0.! !


!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
gap

        ^ gap! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
gap: anObject

        gap := anObject! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
pw

        ^ pw! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
pw: anObject

        pw := anObject! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
lw

        ^ lw! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
lw: anObject

        lw := anObject! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
rw

        ^ rw! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
rw: anObject

        rw := anObject! !

'From Squeak4.5 of 19 February 2014 [latest update: #13680] on 30 September 2015 at 10:53:31 am'!
Benchmark subclass: #ConstraintsBenchmarks
        instanceVariableNames: 'obj constrObj constraints'
        classVariableNames: ''
        poolDictionaries: ''
        category: 'Constraints-Benchmarks'!

!ConstraintsBenchmarks methodsFor: 'benchmarks' stamp: 'tfel 9/23/2015 15:42'!
benchLayout

10 timesRepeat: [
obj := ConstraintMockObject new.
[ obj pw = 40000 ] alwaysTrue.
[ obj gap = (obj pw / 20000) ] alwaysTrue.
[ obj lw + obj gap + obj rw = obj pw ] alwaysTrue.
[ obj lw >= 0 ] alwaysTrue.
[ obj rw >= 0 ] alwaysTrue.
FileStream stdout
nextPutAll: 'gap = ', obj gap, ', pw = ', obj pw, ' lw = ', obj lw, ' rw = ', obj rw;
crlf; flush.].

! !

| a |
FileStream stdout nextPutAll: 'Run'; crlf; flush.
a := (ConstraintsBenchmarks run: 1).
FileStream stdout nextPutAll: 'THIS IS THE TIME: '; nextPutAll: (a results anyOne first total asString); crlf; flush.
Smalltalk snapshot: false andQuit: true.!

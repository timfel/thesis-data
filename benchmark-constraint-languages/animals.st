'From Squeak4.5 of 19 February 2014 [latest update: #13680] on 5 October 2015 at 11:56:17 am'!
!ConstraintZ3Variable methodsFor: 'initialize-release' stamp: 'tfel 10/5/2015 13:33'!
initialize
    "Use integers"
    varName := 'noName'.
    type := 'Int'.! !

Object subclass: #AnimalsObject
        instanceVariableNames: 'cents animals dogc catc micec dog cat mouse'
        classVariableNames: ''
        poolDictionaries: ''
        category: 'Constraints-Benchmarks'!

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
animals

        ^ animals! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
animals: anObject

        animals := anObject! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
cat

        ^ cat! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
cat: anObject

        cat := anObject! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
catc

        ^ catc! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
catc: anObject

        catc := anObject! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
cents

        ^ cents! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
cents: anObject

        cents := anObject! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
dog

        ^ dog! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
dog: anObject

        dog := anObject! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
dogc

        ^ dogc! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
dogc: anObject

        dogc := anObject! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
micec

        ^ micec! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
micec: anObject

        micec := anObject! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
mouse

        ^ mouse! !

!AnimalsObject methodsFor: 'accessing' stamp: 'tfel 10/5/2015 11:45'!
mouse: anObject

        mouse := anObject! !



!AnimalsObject methodsFor: 'initialize-release' stamp: 'tfel 10/5/2015 11:46'!
initialize

        animals := 0.
        cat := 0.
        catc := 0.
        cents := 0.
        dog := 0.
        dogc := 0.
        micec := 0.
        mouse := 0.! !


'From Squeak4.5 of 19 February 2014 [latest update: #13680] on 5 October 2015 at 12:01:34 pm'!
Benchmark subclass: #ConstraintsBenchmarks
        instanceVariableNames: 'obj'
        classVariableNames: ''
        poolDictionaries: ''
        category: 'Constraints-Benchmarks'!

!ConstraintsBenchmarks methodsFor: 'nil' stamp: 'tfel 10/5/2015 12:01'!
benchAnimals
50 timesRepeat: [
        | solver |
        obj := AnimalsObject new.
        solver := ConstraintSolver newZ3Solver.
        [ (obj cents = 10000) &
                (obj animals = 100) & (
                        obj dogc = 1500) & (
                                obj catc = 100) & (
                                        obj micec = 25) ] alwaysSolveWith: solver.
        [ obj dog >= 1 & ( obj cat >= 1 ) & ( obj mouse >= 1) ] alwaysSolveWith: solver.
        [ obj dog + obj cat + obj mouse = obj animals ] alwaysSolveWith: solver.
        [ (obj dog * obj dogc) + (obj cat * obj catc) + (obj mouse * obj micec) = obj cents ] alwaysSolveWith: solver.
        FileStream stdout nextPutAll: 'Dogs: ', obj dog, ', cats: ', obj cat , ', mice: ', obj mouse; cr; flush].
! !

FileStream stdout nextPutAll: 'Run'; crlf; flush.!
FileStream stdout nextPutAll: (ConstraintsBenchmarks run: 10) asString; crlf; flush.!
Smalltalk snapshot: false andQuit: true.!

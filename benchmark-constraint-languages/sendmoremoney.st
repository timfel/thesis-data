'From Squeak4.5 of 19 February 2014 [latest update: #13680] on 5 October 2015 at 11:56:17 am'!
!ConstraintZ3Variable methodsFor: 'initialize-release' stamp: 'tfel 10/5/2015 13:33'!
initialize
    "Use integers"
    varName := 'noName'.
    type := 'Int'.! !

'From Squeak4.5 of 19 February 2014 [latest update: #13680] on 5 October 2015 at 1:48:46 pm'!
Object subclass: #SMM
	instanceVariableNames: 'ary'
	classVariableNames: ''
	poolDictionaries: ''
	category: 'Constraints-Benchmarks'!

!SMM methodsFor: 'initialize-release' stamp: 'tfel 10/5/2015 13:45'!
initialize

	ary := {0. 0. 0. 0. 0. 0. 0. 0}! !

!SMM methodsFor: 'initialize-release' stamp: 'tfel 10/5/2015 13:45'!
d

	^ ary at: 4! !

!SMM methodsFor: 'initialize-release' stamp: 'tfel 10/5/2015 13:45'!
e

	^ ary at: 2! !

!SMM methodsFor: 'initialize-release' stamp: 'tfel 10/5/2015 13:45'!
m

	^ ary at: 5! !

!SMM methodsFor: 'initialize-release' stamp: 'tfel 10/5/2015 13:45'!
n

	^ ary at: 3! !

!SMM methodsFor: 'initialize-release' stamp: 'tfel 10/5/2015 13:45'!
o

	^ ary at: 6! !

!SMM methodsFor: 'initialize-release' stamp: 'tfel 10/5/2015 13:45'!
r

	^ ary at: 7! !

!SMM methodsFor: 'initialize-release' stamp: 'tfel 10/5/2015 13:45'!
s

	^ ary at: 1! !

!SMM methodsFor: 'initialize-release' stamp: 'tfel 10/5/2015 13:45'!
y

	^ ary at: 8! !


!SMM methodsFor: 'as yet unclassified' stamp: 'tfel 10/5/2015 13:46'!
ary

	^ ary! !

!SMM methodsFor: 'as yet unclassified' stamp: 'tfel 10/5/2015 13:46'!
ary: anArray

	ary := anArray.! !

'From Squeak4.5 of 19 February 2014 [latest update: #13680] on 5 October 2015 at 1:48:48 pm'!
Benchmark subclass: #ConstraintBenchmarks
	instanceVariableNames: ''
	classVariableNames: ''
	poolDictionaries: ''
	category: 'Constraints-Benchmarks'!

!ConstraintBenchmarks methodsFor: 'as yet unclassified' stamp: 'tfel 10/5/2015 13:48'!
benchSendMoreMoney
	| solver p |
	50 timesRepeat: [
		p := SMM new.
		solver := ConstraintSolver newZ3Solver.
		[p ary allSatisfy: [:ea | (ea <= 9) & (ea >= 0)]] alwaysSolveWith: solver.
		[p ary allDifferent] alwaysSolveWith: solver.
		[		((p s * 1000) + (p e * 100) + (p n * 10) + (p d) +
				(p m * 1000) + (p o * 100) + (p r * 10) + (p e)) =
		((p m * 10000) + (p o * 1000) + (p n * 100) + (p e * 10) + (p y))
		] alwaysSolveWith: solver.
		[(p s > 0) & (p m > 0)] alwaysSolveWith: solver.
		FileStream stdout nextPutAll: 'solution: ', p ary; cr; flush.
	]! !

| a|
FileStream stdout nextPutAll: 'Run'; crlf; flush.!
a := (ConstraintBenchmarks run: 1).
FileStream stdout nextPutAll: 'THIS IS THE TIME: '; nextPutAll: (a results anyOne first total asString); crlf; flush.
Smalltalk snapshot: false andQuit: true.!

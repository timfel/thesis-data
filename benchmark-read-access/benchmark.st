'From Squeak4.5 of 19 February 2014 [latest update: #13680] on 30 September 2015 at 11:09:18 am'!
Object subclass: #ConstraintMockObject
	instanceVariableNames: 'a b c d e'
	classVariableNames: ''
	poolDictionaries: ''
	category: 'Constraints-Benchmarks'!

!ConstraintMockObject methodsFor: 'initialize-release' stamp: 'tfel 9/23/2015 15:38'!
initialize

	a := 1.
	b := 1.
	c := 1.
	d := 1.
	e := 1.! !


!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
a

	^ a! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
a: anObject

	a := anObject! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
b

	^ b! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
b: anObject

	b := anObject! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
c

	^ c! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
c: anObject

	c := anObject! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
d

	^ d! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
d: anObject

	d := anObject! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
e

	^ e! !

!ConstraintMockObject methodsFor: 'accessing' stamp: 'tfel 9/23/2015 15:38'!
e: anObject

	e := anObject! !

'From Squeak4.5 of 19 February 2014 [latest update: #13680] on 30 September 2015 at 10:53:31 am'!
Benchmark subclass: #ConstraintsBenchmarks
	instanceVariableNames: 'obj constrObj constraints'
	classVariableNames: ''
	poolDictionaries: ''
	category: 'Constraints-Benchmarks'!

!ConstraintsBenchmarks methodsFor: 'benchmarks' stamp: 'tfel 9/23/2015 15:42'!
benchConstrainedReadAccess

	1000 timesRepeat: [
		constrObj a + constrObj b + constrObj c + constrObj d + constrObj e
	]! !

!ConstraintsBenchmarks methodsFor: 'benchmarks' stamp: 'tfel 9/23/2015 15:47'!
benchConstrainedReadAccessDisabled

	constraints do: #disable.
	1000 timesRepeat: [
		constrObj a + constrObj b + constrObj c + constrObj d + constrObj e
	]! !

!ConstraintsBenchmarks methodsFor: 'benchmarks' stamp: 'tfel 9/23/2015 15:39'!
benchReadAccess

	1000 timesRepeat: [
		obj a + obj b + obj c + obj d + obj e
	]! !


!ConstraintsBenchmarks methodsFor: 'running' stamp: 'tfel 9/23/2015 15:46'!
setUp

	obj := ConstraintMockObject new.
	constrObj := ConstraintMockObject new.
	constraints := OrderedCollection new.
	constraints add: [constrObj a = 1] alwaysTrue.
	constraints add: [constrObj b = 1] alwaysTrue.
	constraints add: [constrObj c = 1] alwaysTrue.
	constraints add: [constrObj d = 1] alwaysTrue.
	constraints add: [constrObj e = 1] alwaysTrue.
! !

FileStream stdout nextPutAll: 'Warmup'; crlf; flush.!
FileStream stdout nextPutAll: (ConstraintsBenchmarks run: 10) asString; crlf; flush.!
FileStream stdout crlf; crlf; nextPutAll: 'Run'; crlf; flush.!
FileStream stdout nextPutAll: (ConstraintsBenchmarks run: 100) asString; crlf; flush.!
Smalltalk snapshot: false andQuit: true; crlf; flush.!

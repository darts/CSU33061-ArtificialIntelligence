:- (dynamic kb/1).

makeKB(File) :-
    open(File, read, Str),
    readK(Str, K),
    reformat(K, KB),
    asserta(kb(KB)),
    close(Str).                  
   
readK(Stream, []) :-
    at_end_of_stream(Stream),
    !.
readK(Stream, [X|L]) :-
    read(Stream, X),
    readK(Stream, L).

reformat([], []).

reformat([end_of_file], []) :-
    !.

reformat([(H:-B)|L], [[H|BL]|R]) :-
    !,
    mkList(B, BL),
    reformat(L, R).

reformat([A|L], [[A]|R]) :-
    reformat(L, R).
    
mkList((X, T), [X|R]) :-
    !,
    mkList(T, R).

mkList(X, [X]).

initKB(File) :-
    retractall(kb(_)),
    makeKB(File).

%-----------------------------------------------------------

%user input
astar(Node, Path, Cost) :-
    kb(KB),
    astar([[Node, [], 0]], Path, Cost, KB).

%final node reached
astar([[Node, Path, Cost]|_], [Node, Path], Cost, _) :-
    goal(Node).

%some still unexplored
astar([[Node, NP, NC]|Rest], Path, Cost, KB) :-
    findall([P, [Node|NP], Sum],
            ( arc(Node, P, Q, KB),
              Sum is Q+NC
            ),
            Children),
    add-to-frontier(Children, Rest, New),
    astar(New, Path, Cost, KB).

add-to-frontier(Children, More, New) :-
    append(Children, More, Tmp),
    sortByMin(Tmp, New).

%need to include heuristic function in sort
sortByMin([OldH|OldT], New) :-
    sortByMinRec(OldH, [], OldT, New).
% sortByMin(Old, New) :- sort(Old, New).

%list is empty, all sorted
sortByMinRec(H, Rem, [], [H|Rem]).
%list is not empty, sort
sortByMinRec(H, Swp, [RemH|RemT], New) :-
    (   lessThan(H, RemH),
        !,
        sortByMinRec(H, [RemH|Swp], RemT, New)
    ;   sortByMinRec(RemH, [H|Swp], RemT, New)
    ).

%-----------------------------------------------------------
lessThan([[Node1|_], Cost1], [[Node2|_], Cost2]) :-
    heuristic(Node1, Hvalue1),
    heuristic(Node2, Hvalue2),
    F1 is Cost1+Hvalue1,
    F2 is Cost2+Hvalue2,
    F1=<F2.

arc([H|T], Node, Cost, KB) :-
    member([H|B], KB),
    append(B, T, Node),
    length(B, L),
    Cost is L+1.

heuristic(Node, H) :-
    length(Node, H).

goal([]).

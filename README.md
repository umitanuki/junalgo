## Setup

Set API key environment variables.

```
export APCA_API_KEY_ID=xxx
export APCA_API_SECRET_KEY=xxx
```

It is packaged in a docker, so setup should be done by building the image.

```
$ make build
```


## Run

```
$ make run
```

For the debug purpose, you can start a shell by

```
$ make debug
```

## State Management

The algo saves a local file called `.state.json` in this directory and loads
the last state when it restarts.  Docker mounts this current directory.

## Basic Logic Flow

The algo buys the stock for 95% of the cash when one of the current strategies
hits the buy signal. When a position is held, it checks the sell signal of
the buy strategy, and sells everything when it hits the signal.

The strategies are chosen based on the last 6 months daily prices. It simply
runs the backtest for this duration and see the total profit.

The algo is supposed to run once every morning.  The order decision is made
at the market open and places a market order.


## Note

Backtesting of the algo is implemented separately (test1.py). In order to
run this backtesting, you need to install python dependencies by pipenv.

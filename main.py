# GroceryStoreSim.py
# Name: Collin Frederick
# Date: 4/27
# Assignment: Grocery Store Simulation

import simpy
import random

# Global variables
eventLog = []         # Records (shopper_id, items, arrival_time, done_shopping_time, depart_time)
waitingShoppers = []  # Queue of shoppers ready to checkout
idleTime = 0          # Cumulative idle time across all checkers


def shopper(env, id):
    """
    Simulates a shopper: arrives, shops, then joins the checkout queue.
    """
    arrive = env.now
    items = random.randint(5, 20)
    shoppingTime = items // 2  # assume 0.5 minutes per item
    yield env.timeout(shoppingTime)
    # shopper done shopping, join waiting queue
    waitingShoppers.append((id, items, arrive, env.now))


def checker(env, checker_id):
    """
    Simulates a checker: processes shoppers or idles if none are waiting.
    """
    global idleTime
    while True:
        # if no shoppers waiting, accumulate idle time
        while not waitingShoppers:
            idleTime += 1
            yield env.timeout(1)

        # process next shopper in queue
        customer = waitingShoppers.pop(0)
        _, items, arrive, done_shopping = customer
        checkoutTime = items // 10 + 1  # at least 1 minute per transaction
        yield env.timeout(checkoutTime)

        # record final stats
        eventLog.append((customer[0], items, arrive, done_shopping, env.now))


def customerArrival(env, arrival_interval=2):
    """
    Generates shoppers at a steady rate every arrival_interval minutes.
    """
    customerNumber = 0
    while True:
        customerNumber += 1
        env.process(shopper(env, customerNumber))
        yield env.timeout(arrival_interval)


def processResults():
    """
    Processes and prints simulation results, including additional metrics.
    """
    totalShoppers = len(eventLog)

    if totalShoppers == 0:
        print("No shoppers were processed.")
        return

    totalWait = 0
    totalItems = 0
    totalShoppingTime = 0
    maxWait = 0
    maxShoppingTime = 0

    for sid, items, arrive, done_shopping, depart in eventLog:
        waitTime = depart - done_shopping
        shoppingTime = done_shopping - arrive
        totalWait += waitTime
        totalItems += items
        totalShoppingTime += shoppingTime
        if waitTime > maxWait:
            maxWait = waitTime
        if shoppingTime > maxShoppingTime:
            maxShoppingTime = shoppingTime

    avgWait = totalWait / totalShoppers
    avgItems = totalItems / totalShoppers
    avgShoppingTime = totalShoppingTime / totalShoppers

    print(f"Number of shoppers served: {totalShoppers}")
    print(f"Average items per shopper: {avgItems:.2f}")
    print(f"Average shopping time: {avgShoppingTime:.2f} minutes")
    print(f"Average wait time in queue: {avgWait:.2f} minutes")
    print(f"Maximum wait time: {maxWait} minutes")
    print(f"Maximum shopping time: {maxShoppingTime} minutes")
    print(f"Total idle time (all checkers): {idleTime} minutes")


def main():
    # Configuration
    numberCheckers = 5     # how many checkout lines
    simulationTime = 180   # total simulation duration in minutes
    arrivalInterval = 2    # new shopper every X minutes

    # Initialize environment
    env = simpy.Environment()

    # Start processes
    env.process(customerArrival(env, arrivalInterval))
    for i in range(1, numberCheckers + 1):
        env.process(checker(env, i))

    # Run simulation
    env.run(until=simulationTime)

    # Report any shoppers still waiting
    if waitingShoppers:
        print(f"Shoppers left in queue: {len(waitingShoppers)}")
    else:
        print("No shoppers left waiting.")

    # Process and display results
    processResults()


if __name__ == '__main__':
    main()
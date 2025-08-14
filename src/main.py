from agents import set_tracing_disabled
import asyncio

set_tracing_disabled(disabled=True)

def main():
    print("Hello from deepsearch!")


if __name__ == "__main__":
    asyncio.run(main())

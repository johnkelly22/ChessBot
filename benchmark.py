import time
import board
import moves
import minimax

def run_benchmark():
    print("Starting Benchmark...")
    
    # Setup board
    bb = board.bb.copy()
    
    # Benchmark Depth 3
    start_time = time.time()
    minimax.find_best_move(bb, 3)
    end_time = time.time()
    print(f"Depth 3: {end_time - start_time:.4f} seconds")
    
    # Benchmark Depth 4
    start_time = time.time()
    minimax.find_best_move(bb, 4)
    end_time = time.time()
    print(f"Depth 4: {end_time - start_time:.4f} seconds")

    # Benchmark Depth 5
    print("Running Depth 5 (this might take a little longer)...")
    start_time = time.time()
    minimax.find_best_move(bb, 5)
    end_time = time.time()
    print(f"Depth 5: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    run_benchmark()

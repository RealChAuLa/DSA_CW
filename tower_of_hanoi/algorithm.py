# Tower of Hanoi Algorithms
import math


def hanoi_recursive_3peg(n, source='A', target='C', auxiliary='B'):
    """3-peg recursive solution - O(2^n), minimum moves = 2^n - 1"""
    if not isinstance(n, int) or n < 0:
        raise ValueError("Number of disks must be a non-negative integer")
    if n == 0:
        return []
    
    moves = []
    
    def solve(n, src, tgt, aux):
        # Base case: single disk
        if n == 1:
            moves.append((src, tgt))
            return
        # Recursive: move n-1 to aux, move largest to target, move n-1 to target
        solve(n - 1, src, aux, tgt)
        moves.append((src, tgt))
        solve(n - 1, aux, tgt, src)
    
    solve(n, source, target, auxiliary)
    return moves


def hanoi_iterative_3peg(n, source='A', target='C', auxiliary='B'):
    """3-peg iterative pattern-based solution - O(2^n), alternates smallest disk moves"""
    if not isinstance(n, int) or n < 0:
        raise ValueError("Number of disks must be a non-negative integer")
    if n == 0:
        return []
    
    moves = []
    towers = {source: list(range(n, 0, -1)), auxiliary: [], target: []}
    
    # Peg order depends on parity
    pegs = [source, target, auxiliary] if n % 2 == 1 else [source, auxiliary, target]
    total = (2 ** n) - 1
    pos = 0
    
    for i in range(total):
        if i % 2 == 0:
            # Move smallest disk cyclically
            frm = pegs[pos]
            pos = (pos + 1) % 3
            to = pegs[pos]
            towers[to].append(towers[frm].pop())
            moves.append((frm, to))
        else:
            # Make only legal move not involving smallest disk
            others = [p for p in [source, auxiliary, target] 
                      if not towers[p] or towers[p][-1] != 1]
            if not towers[others[0]]:
                frm, to = others[1], others[0]
            elif not towers[others[1]]:
                frm, to = others[0], others[1]
            elif towers[others[0]][-1] < towers[others[1]][-1]:
                frm, to = others[0], others[1]
            else:
                frm, to = others[1], others[0]
            towers[to].append(towers[frm].pop())
            moves.append((frm, to))
    
    return moves


def hanoi_frame_stewart(n, source='A', target='D', aux1='B', aux2='C'):
    """4-peg Frame-Stewart algorithm - O(2^sqrt(2n)), uses DP for optimal k"""
    if not isinstance(n, int) or n < 0:
        raise ValueError("Number of disks must be a non-negative integer")
    if n == 0:
        return []
    
    moves = []
    
    # DP to find optimal split point k
    dp = {0: 0, 1: 1}
    k_opt = {0: 0, 1: 0}
    
    for i in range(2, n + 1):
        dp[i] = float('inf')
        for k in range(1, i):
            cost = 2 * dp[k] + (2 ** (i - k)) - 1
            if cost < dp[i]:
                dp[i] = cost
                k_opt[i] = k
    
    def three_peg(n, src, tgt, aux):
        """Standard 3-peg recursive helper"""
        if n == 0:
            return
        if n == 1:
            moves.append((src, tgt))
            return
        three_peg(n - 1, src, aux, tgt)
        moves.append((src, tgt))
        three_peg(n - 1, aux, tgt, src)
    
    def four_peg(n, src, tgt, a1, a2):
        """4-peg recursive using Frame-Stewart strategy"""
        if n == 0:
            return
        if n == 1:
            moves.append((src, tgt))
            return
        
        k = k_opt[n]
        four_peg(k, src, a2, a1, tgt)      # Move k disks to aux2 using 4 pegs
        three_peg(n - k, src, tgt, a1)     # Move n-k disks to target using 3 pegs
        four_peg(k, a2, tgt, src, a1)      # Move k disks to target using 4 pegs
    
    four_peg(n, source, target, aux1, aux2)
    return moves

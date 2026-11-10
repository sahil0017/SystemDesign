public class LRUCacheDemo {
    public static void main(String[] args) {
        System.out.println("=== LRU Cache Demo ===\n");

        LRUCache<String, Integer> cache = new LRUCache<>(3);

        System.out.println("1. Adding items to cache (capacity = 3)");
        cache.put("a", 1);
        System.out.println("   put('a', 1)");
        cache.put("b", 2);
        System.out.println("   put('b', 2)");
        cache.put("c", 3);
        System.out.println("   put('c', 3)");
        System.out.println("   Cache state: {a=1, b=2, c=3}");

        System.out.println("\n2. Accessing 'a' makes it most recently used");
        Integer valueA = cache.get("a");
        System.out.println("   get('a') = " + valueA);
        System.out.println("   Order now: b (LRU) -> c -> a (MRU)");

        System.out.println("\n3. Adding 'd' should evict 'b' (the LRU item)");
        cache.put("d", 4);
        System.out.println("   put('d', 4)");
        Integer valueB = cache.get("b");
        System.out.println("   get('b') = " + valueB + " (null means evicted)");

        System.out.println("\n4. Verifying other items still accessible");
        System.out.println("   get('c') = " + cache.get("c"));
        System.out.println("   get('a') = " + cache.get("a"));
        System.out.println("   get('d') = " + cache.get("d"));

        System.out.println("\n5. Updating existing key");
        cache.put("c", 30);
        System.out.println("   put('c', 30) - updates value and marks as MRU");
        System.out.println("   get('c') = " + cache.get("c"));

        System.out.println("\n6. Adding 'e' should evict 'a' (now the LRU)");
        cache.put("e", 5);
        System.out.println("   put('e', 5)");
        System.out.println("   get('a') = " + cache.get("a") + " (null means evicted)");
        System.out.println("   get('d') = " + cache.get("d"));

        System.out.println("\n=== Demo Complete ===");
    }
}

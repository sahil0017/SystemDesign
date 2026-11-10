import java.util.HashMap;
import java.util.Map;

public class LRUCache <K,V> {
    private final int capacity;
    private final Map<K, Node<K,V>> map;
    private final DoublyLinkedList<K,V> list;

    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.map = new HashMap<>();
        this.list = new DoublyLinkedList<>();
    }

    public synchronized V get(K key) {
        if (!map.containsKey(key)) {
            return null;
        }

        Node<K, V> node = map.get(key);
        list.moveToFront(node);
        return node.val;
    }

    public synchronized void put(K key, V value) {
        if (map.containsKey(key)) {
            // Update existing entry
            Node<K, V> node = map.get(key);
            node.val = value;
            list.moveToFront(node);
        } else {
            // Add new entry
            if (map.size() == capacity) {
                // Evict LRU item
                Node<K, V> lru = list.removeLast();
                if (lru != null) {
                    map.remove(lru.key);
                }
            }

            Node<K, V> newNode = new Node<>(key, value);
            list.addFirst(newNode);
            map.put(key, newNode);
        }
    }
}

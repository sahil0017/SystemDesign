public class Node <K,V> {
    K key;
    V val;

    Node<K,V> prev;
    Node<K,V> next;

    Node(K key, V val) {
        this.key = key;
        this.val = val;
    }
}

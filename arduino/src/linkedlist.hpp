#pragma clang diagnostic ignored "-Wpragma-once-outside-header"
#pragma once
#include <stdint.h>

template<class T> class ListElement {
public:
    ListElement(T element) {
        content = element;
        prev_element = nullptr;
        next_element = nullptr;
    };
    ~ListElement() {
        if (prev_element) prev_element->next_element = next_element;
        if (next_element) next_element->prev_element = prev_element;
    };
    T content;
    ListElement<T> *next_element;
    ListElement<T> *prev_element;
};

template<class T> class List {
public:
    List() {
        first_element = nullptr;
        current_element = nullptr;
    };
    List(List<T>&& other) {  // move
        first_element = other.first_element;
        current_element = other.current_element;
    };
    ~List() {
        to_begin();
        while (current_element) {
            ListElement<T> *temp = current_element->next_element;
            delete current_element;
            current_element = temp;
        }
        first_element = nullptr;
        current_element = nullptr;
    };
    void insert_next(T element) {
        if(current_element) {
            ListElement<T>* old_next = current_element->next_element;
            ListElement<T>* new_next = new ListElement<T>(element);
            new_next->prev_element = current_element;
            new_next->next_element = old_next;
            current_element->next_element = new_next;
            if (old_next) old_next->prev_element = new_next;
            else last_element = new_next;
            to_next();
        } else {
            current_element = new ListElement<T>(element);
            first_element = current_element;
            last_element = current_element;
        }
    };
    void insert_prev(T element) {
        if(current_element) {
            ListElement<T>* old_prev = current_element->prev_element;
            ListElement<T>* new_prev = new ListElement<T>(element);
            new_prev->next_element = current_element;
            new_prev->prev_element = old_prev;
            current_element->prev_element = new_prev;
            if (old_prev) old_prev->next_element = new_prev;
            else first_element = new_prev;
            to_prev();
        } else {
            current_element = new ListElement<T>(element);
            first_element = current_element;
            last_element = current_element;
        }
    };
    void remove() {
        if(!is_empty()) {
            ListElement<T>* temp = current_element;
            if (current_element == first_element) {
                first_element = temp->next_element;
                current_element = current_element->next_element;
            } else {
                if (current_element == last_element) last_element = temp->prev_element;
                current_element = current_element->prev_element;
            }
            delete temp;
        }
    };
    bool is_empty() { return current_element == nullptr; };
    void to_begin() { current_element = first_element; };
    bool to_next() {
        if (current_element == nullptr) return false;
        if (current_element->next_element) {
            current_element = current_element->next_element;
            return true;
        } else return false;
    };
    bool to_prev() {
        if (current_element == nullptr) return false;
        if (current_element->prev_element) {
            current_element = current_element->prev_element;
            return true;
        } else return false;
    };
    T get_value() { return current_element->content; };
private:
    ListElement<T> *first_element;
    ListElement<T> *last_element;
    ListElement<T> *current_element;
};

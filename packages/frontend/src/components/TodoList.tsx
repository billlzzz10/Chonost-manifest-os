import React, { useState } from 'react';
import { useAppStore } from '../store/appStore';
import { CheckCircle, Circle, Plus, X, Flag } from 'lucide-react';

const TodoList: React.FC = () => {
  const { todos, createTodo, updateTodo, deleteTodo, toggleTodoStatus } = useAppStore();
  const [newTodoTitle, setNewTodoTitle] = useState('');
  const [newTodoDescription, setNewTodoDescription] = useState('');
  const [newTodoPriority, setNewTodoPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [showAddForm, setShowAddForm] = useState(false);

  const handleAddTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newTodoTitle.trim()) {
      await createTodo(newTodoTitle.trim(), newTodoDescription.trim(), newTodoPriority);
      setNewTodoTitle('');
      setNewTodoDescription('');
      setNewTodoPriority('medium');
      setShowAddForm(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-500';
      case 'medium': return 'text-yellow-500';
      case 'low': return 'text-green-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'in_progress': return 'text-blue-600';
      case 'pending': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 max-w-md mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-800">Todo List</h2>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="p-2 text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
        >
          <Plus size={20} />
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleAddTodo} className="mb-4 p-4 bg-gray-50 rounded-lg">
          <input
            type="text"
            value={newTodoTitle}
            onChange={(e) => setNewTodoTitle(e.target.value)}
            placeholder="Todo title..."
            className="w-full p-2 mb-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          <textarea
            value={newTodoDescription}
            onChange={(e) => setNewTodoDescription(e.target.value)}
            placeholder="Description (optional)..."
            className="w-full p-2 mb-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={2}
          />
          <div className="flex items-center justify-between">
            <select
              value={newTodoPriority}
              onChange={(e) => setNewTodoPriority(e.target.value as 'low' | 'medium' | 'high')}
              className="p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
            </select>
            <div className="flex gap-2">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                Add
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </form>
      )}

      <div className="space-y-2">
        {todos.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No todos yet. Add one above!</p>
        ) : (
          todos.map((todo) => (
            <div
              key={todo.id}
              className={`p-3 border rounded-lg transition-all ${
                todo.status === 'completed' ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'
              }`}
            >
              <div className="flex items-start gap-3">
                <button
                  onClick={() => toggleTodoStatus(todo.id)}
                  className={`mt-1 ${getStatusColor(todo.status)} hover:opacity-75 transition-opacity`}
                >
                  {todo.status === 'completed' ? (
                    <CheckCircle size={20} />
                  ) : (
                    <Circle size={20} />
                  )}
                </button>

                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className={`font-medium ${todo.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-800'}`}>
                      {todo.title}
                    </h3>
                    <Flag size={14} className={getPriorityColor(todo.priority)} />
                  </div>

                  {todo.description && (
                    <p className={`text-sm ${todo.status === 'completed' ? 'text-gray-400' : 'text-gray-600'}`}>
                      {todo.description}
                    </p>
                  )}

                  <div className="flex items-center justify-between mt-2">
                    <span className={`text-xs px-2 py-1 rounded ${getStatusColor(todo.status)} bg-opacity-10`}>
                      {todo.status.replace('_', ' ')}
                    </span>
                    <button
                      onClick={() => deleteTodo(todo.id)}
                      className="text-red-500 hover:text-red-700 transition-colors"
                    >
                      <X size={16} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default TodoList;
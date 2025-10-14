import React from 'react';
import { Prompt } from '../types';

interface PromptCardProps {
  prompt: Prompt;
  onEdit: (prompt: Prompt) => void;
  onDelete: (promptId: string) => void;
  onDuplicate: (prompt: Prompt) => void;
}

export const PromptCard: React.FC<PromptCardProps> = ({
  prompt,
  onEdit,
  onDelete,
  onDuplicate,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{prompt.title}</h3>
        <div className="flex space-x-2">
          <button
            onClick={() => onEdit(prompt)}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            Edit
          </button>
          <button
            onClick={() => onDuplicate(prompt)}
            className="text-green-600 hover:text-green-800 text-sm"
          >
            Duplicate
          </button>
          <button
            onClick={() => onDelete(prompt.id)}
            className="text-red-600 hover:text-red-800 text-sm"
          >
            Delete
          </button>
        </div>
      </div>
      
      <p className="text-gray-600 mb-4 line-clamp-3">{prompt.content}</p>
      
      <div className="flex flex-wrap gap-2 mb-4">
        <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
          {prompt.category}
        </span>
        {prompt.tags.map((tag) => (
          <span
            key={tag}
            className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded"
          >
            {tag}
          </span>
        ))}
      </div>
      
      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>Used {prompt.usageCount} times</span>
        <span>Updated {prompt.updatedAt.toLocaleDateString()}</span>
      </div>
    </div>
  );
};

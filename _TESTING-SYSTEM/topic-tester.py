#!/usr/bin/env python3
"""
Topic Tester - Main CLI Interface for Knowledge Testing System

Interactive command-line interface for testing knowledge across any folder.
Supports multiple difficulty levels, progress tracking, and personalized recommendations.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.prompt import Prompt, Confirm
from rich import print as rprint

# Import our custom modules
from question_generator import QuestionGenerator, Question
from answer_evaluator import AnswerEvaluator, EvaluationResult, EvaluationTier


class TestSession:
    """Manages a single testing session."""
    
    def __init__(self, folder_path: str, config_path: Optional[str] = None):
        self.folder_path = Path(folder_path)
        self.config_path = config_path
        self.console = Console()
        
        # Initialize components
        self.question_generator = QuestionGenerator(config_path)
        self.answer_evaluator = AnswerEvaluator(config_path)
        
        # Session data
        self.questions: List[Question] = []
        self.results: List[Dict] = []
        self.start_time = datetime.now()
        
    def run_test(self, num_questions: int = 10, difficulty: Optional[str] = None, 
                focus_areas: Optional[List[str]] = None, mixed_test: bool = False):
        """Run a complete test session."""
        
        # Welcome message
        self._display_welcome()
        
        # Generate questions
        with self.console.status("[bold green]Generating questions..."):
            if mixed_test:
                self.questions = self._generate_mixed_questions(num_questions)
            else:
                self.questions = self.question_generator.generate_questions_from_folder(
                    str(self.folder_path), num_questions
                )
            
            if difficulty:
                self.questions = [q for q in self.questions if q.difficulty == difficulty][:num_questions]
            
            if focus_areas:
                # Filter questions related to focus areas
                filtered = []
                for question in self.questions:
                    if any(area.lower() in question.question.lower() or 
                          area.lower() in question.expected_answer.lower() 
                          for area in focus_areas):
                        filtered.append(question)
                self.questions = filtered[:num_questions]
        
        if not self.questions:
            self.console.print("[red]No questions generated. Check your folder path and TERMS.md file.[/red]")
            return
        
        self.console.print(f"[green]Generated {len(self.questions)} questions from {self.folder_path.name}[/green]")
        
        # Run the test
        self._run_interactive_test()
        
        # Show results
        self._display_results()
        
        # Ask about saving results
        if Confirm.ask("Save test results?"):
            self._save_results()
    
    def _display_welcome(self):
        """Display welcome message and folder info."""
        folder_name = self.folder_path.name
        folder_category = self._determine_folder_category()
        
        welcome_panel = Panel(
            f"[bold blue]Welcome to Knowledge Tester[/bold blue]\n\n"
            f"Testing Folder: [cyan]{folder_name}[/cyan]\n"
            f"Category: [yellow]{folder_category}[/yellow]\n"
            f"Time: [green]{self.start_time.strftime('%Y-%m-%d %H:%M')}[/green]",
            title="🎯 Knowledge Testing Session",
            border_style="blue"
        )
        self.console.print(welcome_panel)
    
    def _determine_folder_category(self) -> str:
        """Determine the category of the folder being tested."""
        folder_name = self.folder_path.name.lower()
        
        if 'bible' in folder_name or 'theology' in folder_name:
            return 'Reformed Theology & Bible Study'
        elif 'unity' in folder_name:
            return 'Unity Game Development'
        elif 'csharp' in folder_name or 'c#' in folder_name:
            return 'C# Programming'
        elif 'ai' in folder_name or 'llm' in folder_name:
            return 'AI/LLM Automation'
        elif 'soft-skill' in folder_name:
            return 'Professional Development'
        else:
            return 'General Knowledge'
    
    def _generate_mixed_questions(self, num_questions: int) -> List[Question]:
        """Generate questions from multiple folders."""
        # This would be implemented to handle multiple folders
        # For now, just use the single folder
        return self.question_generator.generate_questions_from_folder(
            str(self.folder_path), num_questions
        )
    
    def _run_interactive_test(self):
        """Run the interactive question-answer session."""
        total_questions = len(self.questions)
        
        for i, question in enumerate(self.questions, 1):
            self.console.print(f"\n[bold cyan]Question {i} of {total_questions}[/bold cyan]")
            self.console.print(f"[bold]Category:[/bold] {question.category}")
            self.console.print(f"[bold]Difficulty:[/bold] {question.difficulty}")
            self.console.print(f"[bold]Type:[/bold] {question.question_type}")
            
            # Display the question
            question_panel = Panel(
                question.question,
                title="❓ Question",
                border_style="cyan"
            )
            self.console.print(question_panel)
            
            # Get user's answer
            user_answer = Prompt.ask("\n[bold green]Your answer[/bold green]")
            
            if not user_answer.strip():
                user_answer = "[No answer provided]"
            
            # Evaluate the answer
            with self.console.status("[bold yellow]Evaluating your answer..."):
                evaluation = self.answer_evaluator.evaluate_answer(
                    question.question,
                    question.expected_answer,
                    user_answer,
                    question.category,
                    question.expected_keywords
                )
            
            # Display evaluation results
            self._display_evaluation(question, user_answer, evaluation)
            
            # Store results
            self.results.append({
                'question_number': i,
                'question': question.question,
                'expected_answer': question.expected_answer,
                'user_answer': user_answer,
                'score': evaluation.score,
                'feedback': evaluation.feedback,
                'tier_used': evaluation.tier_used.value,
                'evaluation_time': evaluation.evaluation_time,
                'difficulty': question.difficulty,
                'category': question.category,
                'question_type': question.question_type
            })
            
            # Continue automatically to next question
            if i < total_questions:
                self.console.print()  # Add spacing between questions
    
    def _display_evaluation(self, question: Question, user_answer: str, evaluation: EvaluationResult):
        """Display evaluation results for a single question."""
        # Determine color based on score
        score_color = "green" if evaluation.score >= 0.8 else "yellow" if evaluation.score >= 0.6 else "red"
        
        # Create evaluation panel
        eval_content = []
        eval_content.append(f"[bold {score_color}]Score: {evaluation.score:.1%}[/bold {score_color}]")
        eval_content.append(f"[dim]Evaluation Method: {evaluation.tier_used.value}[/dim]")
        eval_content.append(f"[dim]Confidence: {evaluation.confidence:.1%}[/dim]")
        eval_content.append(f"[dim]Time: {evaluation.evaluation_time:.1f}s[/dim]")
        
        if evaluation.keyword_matches:
            eval_content.append(f"[green]✓ Keywords found: {', '.join(evaluation.keyword_matches)}[/green]")
        
        eval_content.append(f"\n[bold]Feedback:[/bold]\n{evaluation.feedback}")
        
        if evaluation.improvement_suggestions:
            eval_content.append(f"\n[bold blue]Suggestions:[/bold blue]")
            for suggestion in evaluation.improvement_suggestions:
                eval_content.append(f"• {suggestion}")
        
        evaluation_panel = Panel(
            "\n".join(eval_content),
            title="📊 Evaluation Results",
            border_style=score_color
        )
        self.console.print(evaluation_panel)
        
        # Always show expected answer immediately
        expected_panel = Panel(
            question.expected_answer,
            title="💡 Expected Answer",
            border_style="blue"
        )
        self.console.print(expected_panel)
    
    def _display_results(self):
        """Display comprehensive test results."""
        if not self.results:
            return
        
        # Calculate statistics
        total_score = sum(r['score'] for r in self.results)
        avg_score = total_score / len(self.results)
        passing_score = 0.6
        passed = sum(1 for r in self.results if r['score'] >= passing_score)
        
        # Display summary
        summary_content = [
            f"[bold]Questions Answered:[/bold] {len(self.results)}",
            f"[bold]Average Score:[/bold] {avg_score:.1%}",
            f"[bold]Questions Passed:[/bold] {passed}/{len(self.results)} ({passing_score:.0%} threshold)",
            f"[bold]Total Time:[/bold] {(datetime.now() - self.start_time).total_seconds():.0f} seconds"
        ]
        
        summary_color = "green" if avg_score >= 0.8 else "yellow" if avg_score >= 0.6 else "red"
        summary_panel = Panel(
            "\n".join(summary_content),
            title="📈 Test Summary",
            border_style=summary_color
        )
        self.console.print(summary_panel)
        
        # Display detailed results table
        table = Table(title="Detailed Results")
        table.add_column("Q#", style="cyan", width=3)
        table.add_column("Category", style="blue", width=15)
        table.add_column("Difficulty", style="yellow", width=8)
        table.add_column("Score", style="green", width=8)
        table.add_column("Method", style="dim", width=10)
        
        for result in self.results:
            score_str = f"{result['score']:.1%}"
            score_color = "green" if result['score'] >= 0.8 else "yellow" if result['score'] >= 0.6 else "red"
            
            table.add_row(
                str(result['question_number']),
                result['category'][:14],
                result['difficulty'],
                f"[{score_color}]{score_str}[/{score_color}]",
                result['tier_used']
            )
        
        self.console.print(table)
        
        # Performance insights
        self._display_insights()
    
    def _display_insights(self):
        """Display performance insights and recommendations."""
        if not self.results:
            return
        
        insights = []
        
        # Difficulty analysis
        difficulty_scores = {}
        for result in self.results:
            diff = result['difficulty']
            if diff not in difficulty_scores:
                difficulty_scores[diff] = []
            difficulty_scores[diff].append(result['score'])
        
        for difficulty, scores in difficulty_scores.items():
            avg_score = sum(scores) / len(scores)
            insights.append(f"[bold]{difficulty.title()}:[/bold] {avg_score:.1%} average ({len(scores)} questions)")
        
        # Category analysis
        category_scores = {}
        for result in self.results:
            cat = result['category']
            if cat not in category_scores:
                category_scores[cat] = []
            category_scores[cat].append(result['score'])
        
        if len(category_scores) > 1:
            insights.append("\n[bold]By Category:[/bold]")
            for category, scores in category_scores.items():
                avg_score = sum(scores) / len(scores)
                insights.append(f"• {category}: {avg_score:.1%}")
        
        # Recommendations
        insights.append("\n[bold blue]Recommendations:[/bold blue]")
        
        # Find weakest areas
        if difficulty_scores:
            weakest_difficulty = min(difficulty_scores.keys(), 
                                   key=lambda x: sum(difficulty_scores[x]) / len(difficulty_scores[x]))
            insights.append(f"• Focus on {weakest_difficulty} difficulty questions")
        
        if category_scores and len(category_scores) > 1:
            weakest_category = min(category_scores.keys(),
                                 key=lambda x: sum(category_scores[x]) / len(category_scores[x]))
            insights.append(f"• Review {weakest_category} concepts")
        
        # Overall recommendation
        avg_score = sum(r['score'] for r in self.results) / len(self.results)
        if avg_score < 0.6:
            insights.append("• Consider reviewing source materials before retesting")
        elif avg_score < 0.8:
            insights.append("• Good foundation, focus on weaker areas for improvement")
        else:
            insights.append("• Excellent performance! Consider advancing to harder topics")
        
        insights_panel = Panel(
            "\n".join(insights),
            title="🎯 Performance Insights",
            border_style="blue"
        )
        self.console.print(insights_panel)
    
    def _save_results(self):
        """Save test results to file."""
        results_dir = Path("test-results")
        results_dir.mkdir(exist_ok=True)
        
        # Create filename with timestamp
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        folder_name = self.folder_path.name.replace(" ", "_")
        filename = f"{folder_name}_{timestamp}.json"
        filepath = results_dir / filename
        
        # Prepare data to save
        save_data = {
            'test_info': {
                'folder_path': str(self.folder_path),
                'folder_name': self.folder_path.name,
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'total_questions': len(self.results)
            },
            'summary': {
                'average_score': sum(r['score'] for r in self.results) / len(self.results) if self.results else 0,
                'total_score': sum(r['score'] for r in self.results),
                'passed_questions': sum(1 for r in self.results if r['score'] >= 0.6)
            },
            'results': self.results
        }
        
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        self.console.print(f"[green]Results saved to: {filepath}[/green]")


@click.command()
@click.argument('folder_path', type=click.Path(exists=True))
@click.option('--questions', '-q', default=10, help='Number of questions to generate')
@click.option('--difficulty', '-d', type=click.Choice(['easy', 'medium', 'hard']), help='Filter by difficulty')
@click.option('--focus-areas', '-f', help='Comma-separated focus areas')
@click.option('--mixed-test', '-m', is_flag=True, help='Mix questions from multiple folders')
@click.option('--export-results', '-e', help='Export results to specified file')
@click.option('--config', '-c', help='Path to config file')
def main(folder_path, questions, difficulty, focus_areas, mixed_test, export_results, config):
    """
    AI-Powered Knowledge Testing System
    
    Test your knowledge on any folder containing TERMS.md or learning materials.
    
    Examples:
        topic-tester.py ../26-Bible/ --questions 15 --difficulty medium
        topic-tester.py ../01-Unity-Engine/ --focus-areas "GameObjects,Components"  
        topic-tester.py ../26-Bible/ --export-results bible_test_results.json
    """
    # Parse focus areas
    focus_areas_list = None
    if focus_areas:
        focus_areas_list = [area.strip() for area in focus_areas.split(',')]
    
    # Create and run test session
    session = TestSession(folder_path, config)
    session.run_test(
        num_questions=questions,
        difficulty=difficulty,
        focus_areas=focus_areas_list,
        mixed_test=mixed_test
    )


if __name__ == "__main__":
    main()
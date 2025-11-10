import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

void main() {
  runApp(const PizzaReviewsApp());
}

class PizzaReviewsApp extends StatelessWidget {
  const PizzaReviewsApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Pizza Reviews AI',
      theme: ThemeData(primarySwatch: Colors.orange),
      home: const ChatPage(),
    );
  }
}

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final TextEditingController _questionController = TextEditingController();
  late WebSocketChannel _channel;
  String _response = '';
  bool _isLoading = false;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _connectToWebSocket();
  }

  void _connectToWebSocket() {
    try {
      _channel = WebSocketChannel.connect(Uri.parse('ws://localhost:8000/ws'));

      _channel.stream.listen(
            (data) {
          final jsonData = json.decode(data);
          final type = jsonData['type'];
          final text = jsonData['text'] ?? jsonData['message'] ?? '';

          setState(() {
            if (type == 'chunk') {
              _response += text;
            } else if (type == 'error') {
              _error = text;
              _isLoading = false;
            } else if (type == 'done') {
              _isLoading = false;
            }
          });
        },
        onError: (error) {
          setState(() {
            _error = 'Connection error: $error';
            _isLoading = false;
          });
        },
      );
    } catch (e) {
      setState(() {
        _error = 'Failed to connect: $e';
      });
    }
  }

  void _sendQuestion() {
    final question = _questionController.text.trim();
    if (question.isEmpty || _isLoading) return;

    setState(() {
      _response = '';
      _error = '';
      _isLoading = true;
    });

    try {
      _channel.sink.add(json.encode({'question': question}));
    } catch (e) {
      setState(() {
        _error = 'Failed to send question: $e';
        _isLoading = false;
      });
    }
  }

  @override
  void dispose() {
    _channel.sink.close();
    _questionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pizza Reviews AI'),
        backgroundColor: Colors.deepOrange,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Input Section
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _questionController,
                    decoration: const InputDecoration(
                      hintText: 'Ask about pizza reviews...',
                      border: OutlineInputBorder(),
                    ),
                    onSubmitted: (_) => _sendQuestion(),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _sendQuestion,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.deepOrange,
                  ),
                  child: _isLoading
                      ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                      : const Text('Send'),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Error Display
            if (_error.isNotEmpty)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  border: Border.all(color: Colors.red),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  _error,
                  style: const TextStyle(color: Colors.red),
                ),
              ),

            const SizedBox(height: 16),

            // Response Display
            Expanded(
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey[300]!),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: SingleChildScrollView(
                  child: _isLoading && _response.isEmpty
                      ? const Center(child: CircularProgressIndicator())
                      : Text(
                    _response.isEmpty ? 'Ask a question about pizza reviews...' : _response,
                    style: const TextStyle(fontSize: 16),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}